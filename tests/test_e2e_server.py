import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time
import os
import sys

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set env vars for speed
os.environ["REQUEST_DELAY"] = "0.0"
os.environ["RETRY_BASE_DELAY"] = "0.0"

from server import app, state

client = TestClient(app)

@pytest.fixture
def mock_fetch_day_server():
    # Patch fetch_day used by server
    # Note: server.py imports fetch_day inside run_download_job locally
    # But it imports from core.fetch
    with patch('core.fetch.fetch_day') as mock:
        import struct
        import lzma
        # 1 tick
        token = struct.pack('!IIIff', 100, 100000, 99990, 1.5, 1.2)
        data = lzma.compress(token)
        mock.return_value = [(0, data)]
        yield mock

def test_server_download_flow(mock_fetch_day_server):
    # 1. Start Job
    resp = client.post("/api/download", json={
        "symbols": ["EURUSD"],
        "start_date": "2023-01-01",
        "end_date": "2023-01-02",
        "timeframe": "M1"
    })
    assert resp.status_code == 200
    job_id = resp.json()["job_id"]

    # 2. Poll Status
    # Wait for completion (background thread)
    max_retries = 100 # 100 * 0.1 = 10s
    for _ in range(max_retries):
        time.sleep(0.1)
        r = client.get(f"/api/jobs/{job_id}")
        status = r.json()["status"]
        if status in ["completed", "failed"]:
            break

    assert status == "completed"

    # 3. Check Files
    files_resp = client.get("/api/files")
    files = files_resp.json()
    assert len(files) > 0
    filename = files[0]["name"]

    # 4. Download File
    dl_resp = client.get(f"/api/files/{filename}")
    assert dl_resp.status_code == 200

    # Cleanup
    client.delete(f"/api/files/{filename}")
