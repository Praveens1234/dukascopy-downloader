"""
Async HTTP fetcher for Dukascopy bi5 files.
Production-ready with:
  - Browser-like headers (User-Agent, Referer) to avoid 503 blocks
  - Exponential backoff with random jitter on retries
  - Request throttling to prevent server overload
  - Reduced concurrency per day
  - Clean error reporting (no spam)
  - Per-thread event loop reuse (prevents FD exhaustion on long runs)
"""

import asyncio
import random
import threading
from io import BytesIO

import aiohttp

from config.settings import (
    URL_TEMPLATE, HTTP_HEADERS, DOWNLOAD_ATTEMPTS,
    RETRY_BASE_DELAY, RETRY_MAX_DELAY, HOURLY_CONCURRENCY,
    REQUEST_DELAY, HTTP_TIMEOUT, normalize_symbol_for_url,
)
import sys
import socket

# Monkeypatch socket.getaddrinfo to force IPv4
# Prevents connection hangs on machines with broken IPv6 configurations/routing.
orig_getaddrinfo = socket.getaddrinfo
def getaddrinfo_ipv4(*args, **kwargs):
    responses = orig_getaddrinfo(*args, **kwargs)
    ipv4_res = [r for r in responses if r[0] == socket.AF_INET]
    return ipv4_res if ipv4_res else responses
socket.getaddrinfo = getaddrinfo_ipv4

# Set Windows Selector event loop policy to avoid Proactor DNS resolution hangs
if sys.platform == 'win32':
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except AttributeError:
        pass

from utils.logger import get_logger

Logger = get_logger()

# ---------------------------------------------------------------------------
# Thread-local event loop reuse
# ---------------------------------------------------------------------------
# Creating a new event loop per fetch_day() call exhausts OS file descriptors
# on long runs (5+ years).  We keep one loop per thread and reuse it.
_thread_local = threading.local()


def _get_thread_loop():
    """Get or create a reusable event loop for the current thread."""
    loop = getattr(_thread_local, 'loop', None)
    if loop is None or loop.is_closed():
        loop = asyncio.new_event_loop()
        _thread_local.loop = loop
        asyncio.set_event_loop(loop)
    return loop


async def download_hour(session, url, hour, semaphore):
    """
    Download a single hourly bi5 file with exponential backoff + jitter.
    Returns (hour, raw_bytes) tuple.
    """
    async with semaphore:
        last_error = None
        for attempt in range(DOWNLOAD_ATTEMPTS):
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT),
                    headers=HTTP_HEADERS,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return (hour, data)
                    elif resp.status == 404:
                        # No data for this hour (holiday/weekend) — normal
                        return (hour, b"")
                    elif resp.status == 503:
                        # Rate limited — back off aggressively
                        delay = min(
                            RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0.5, 2.0),
                            RETRY_MAX_DELAY
                        )
                        last_error = f"HTTP 503 (rate limited)"
                        await asyncio.sleep(delay)
                    else:
                        delay = RETRY_BASE_DELAY * (attempt + 1) + random.uniform(0, 1)
                        last_error = f"HTTP {resp.status}"
                        await asyncio.sleep(delay)

            except asyncio.TimeoutError:
                delay = RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0.5, 2.0)
                last_error = "timeout"
                await asyncio.sleep(min(delay, RETRY_MAX_DELAY))

            except (aiohttp.ClientError, OSError) as e:
                delay = RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0.5, 2.0)
                last_error = str(e)
                await asyncio.sleep(min(delay, RETRY_MAX_DELAY))

        # All attempts exhausted — log once, return empty (don't crash the whole download)
        Logger.warning(f"Skipped {url.split('/datafeed/')[1]} after {DOWNLOAD_ATTEMPTS} retries ({last_error})")
        return (hour, b"")

async def fetch_day_async(symbol, day, max_concurrent):
    """
    Download all 24 hourly bi5 files for a given day.
    Staggers requests with small delays to avoid rate-limiting.
    Returns list of (hour, raw_bytes) tuples sorted by hour.
    """
    month_0indexed = day.month - 1
    semaphore = asyncio.Semaphore(max_concurrent)

    from aiohttp.resolver import ThreadedResolver
    connector = aiohttp.TCPConnector(
        limit=HOURLY_CONCURRENCY,
        limit_per_host=HOURLY_CONCURRENCY,
        force_close=False,
        enable_cleanup_closed=True,
        resolver=ThreadedResolver(),
    )

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for hour in range(24):
            url = URL_TEMPLATE.format(
                currency=normalize_symbol_for_url(symbol),
                year=day.year,
                month=month_0indexed,
                day=day.day,
                hour=hour,
            )
            tasks.append(download_hour(session, url, hour, semaphore))

            # Stagger requests to avoid burst
            if REQUEST_DELAY > 0:
                await asyncio.sleep(REQUEST_DELAY)

        results = await asyncio.gather(*tasks)

    return sorted(results, key=lambda x: x[0])


def fetch_day(symbol, day, max_concurrent=None):
    """
    Synchronous wrapper for fetch_day_async.
    Returns list of (hour, raw_bytes) tuples.
    Uses a per-thread reusable event loop to avoid FD exhaustion.
    """
    if max_concurrent is None:
        max_concurrent = HOURLY_CONCURRENCY

    loop = _get_thread_loop()
    return loop.run_until_complete(fetch_day_async(symbol, day, max_concurrent))
