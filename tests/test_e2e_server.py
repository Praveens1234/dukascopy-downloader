import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time
import os
import sys
from datetime import datetime

# Add project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set env vars for speed
os.environ["REQUEST_DELAY"] = "0.0"
os.environ["RETRY_BASE_DELAY"] = "0.0"

from server import app, state

client = TestClient(app)

@pytest.fixture
def mock_fetch_native():
    # Patch fetch_native_candles where it is imported in core.service
    with patch('core.service.fetch_native_candles') as mock:
        # Return dummy candles: (datetime, open, high, low, close, volume)
        mock.return_value = [
            (datetime(2023, 1, 1, 0, 0), 1.0, 1.1, 0.9, 1.05, 100),
            (datetime(2023, 1, 1, 0, 1), 1.05, 1.15, 1.0, 1.1, 150),
        ]
        yield mock

def test_server_download_flow(mock_fetch_native):
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
    max_retries = 50 # 5s is plenty with mocks
    status = "pending"
    for _ in range(max_retries):
        time.sleep(0.1)
        r = client.get(f"/api/jobs/{job_id}")
        data = r.json()
        status = data["status"]
        if status in ["completed", "failed"]:
            break

    assert status == "completed"

    # Verify progress reached 100
    r = client.get(f"/api/jobs/{job_id}")
    assert r.json()["progress"] == 100.0

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
