import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from core.fetch import download_hour, fetch_day_async
from core.exceptions import BackoffError

@pytest.mark.asyncio
async def test_download_hour_200():
    # Setup
    session = MagicMock()
    semaphore = asyncio.Semaphore(1)
    url = "http://example.com"
    hour = 10

    # Mock Response
    mock_resp = AsyncMock()
    mock_resp.status = 200
    mock_resp.read.return_value = b"DATA"

    # Mock session.get context manager
    session.get.return_value.__aenter__.return_value = mock_resp

    # Run
    h, data = await download_hour(session, url, hour, semaphore)

    # Assert
    assert h == 10
    assert data == b"DATA"
    session.get.assert_called_once()

@pytest.mark.asyncio
async def test_download_hour_404():
    session = MagicMock()
    semaphore = asyncio.Semaphore(1)

    mock_resp = AsyncMock()
    mock_resp.status = 404
    session.get.return_value.__aenter__.return_value = mock_resp

    h, data = await download_hour(session, "url", 5, semaphore)
    assert h == 5
    assert data == b""

@pytest.mark.asyncio
async def test_download_hour_retry_503_success():
    """Test that it retries on 503 and eventually succeeds."""
    session = MagicMock()
    semaphore = asyncio.Semaphore(1)

    # First response 503, Second 200
    resp1 = AsyncMock()
    resp1.status = 503

    resp2 = AsyncMock()
    resp2.status = 200
    resp2.read.return_value = b"RECOVERED"

    # session.get called multiple times returns different context managers?
    # Or side_effect on the context manager return?
    # session.get() returns a CM. CM.__aenter__ returns response.
    # We need session.get() to return different CMs or same CM that yields different resps?
    # Usually easier to mock side_effect of session.get

    cm1 = MagicMock()
    cm1.__aenter__ = AsyncMock(return_value=resp1)
    cm1.__aexit__ = AsyncMock(return_value=None)

    cm2 = MagicMock()
    cm2.__aenter__ = AsyncMock(return_value=resp2)
    cm2.__aexit__ = AsyncMock(return_value=None)

    session.get.side_effect = [cm1, cm2]

    # Mock sleep to be fast
    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        h, data = await download_hour(session, "url", 1, semaphore)

    assert data == b"RECOVERED"
    assert session.get.call_count == 2

@pytest.mark.asyncio
async def test_download_hour_backoff_error():
    """Test that it raises BackoffError after repeated 503s."""
    session = MagicMock()
    semaphore = asyncio.Semaphore(1)

    # Always 503
    resp = AsyncMock()
    resp.status = 503

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=resp)
    cm.__aexit__ = AsyncMock(return_value=None)

    session.get.return_value = cm

    # We need to ensure loop breaks. DOWNLOAD_ATTEMPTS is 10 (from settings).
    # Mock constants? Or just run it (mock sleep is essential).

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        with pytest.raises(BackoffError):
             await download_hour(session, "url", 1, semaphore)

    # Should be called DOWNLOAD_ATTEMPTS times
    # Actually logic: for attempt in range(DOWNLOAD_ATTEMPTS): ...
    # So call count = DOWNLOAD_ATTEMPTS
    from config.settings import DOWNLOAD_ATTEMPTS
    assert session.get.call_count == DOWNLOAD_ATTEMPTS
