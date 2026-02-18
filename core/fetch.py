"""
Async HTTP fetcher for Dukascopy bi5 files.
Production-ready with:
  - Browser-like headers (User-Agent, Referer) to avoid 503 blocks
  - Exponential backoff with random jitter on retries
  - Request throttling to prevent server overload
  - Reduced concurrency per day
  - Clean error reporting (no spam)
"""

import asyncio
import random
from io import BytesIO

import aiohttp

from config.settings import (
    URL_TEMPLATE, HTTP_HEADERS, DOWNLOAD_ATTEMPTS,
    RETRY_BASE_DELAY, RETRY_MAX_DELAY, HOURLY_CONCURRENCY,
    REQUEST_DELAY, HTTP_TIMEOUT,
)
from core.exceptions import BackoffError
from utils.logger import get_logger

Logger = get_logger()


async def download_hour(session, url, hour, semaphore):
    """
    Download a single hourly bi5 file with exponential backoff + jitter.
    Returns (hour, raw_bytes) tuple.
    """
    async with semaphore:
        last_error = None
        for attempt in range(DOWNLOAD_ATTEMPTS):
            try:
                # Add jitter to timeout to avoid thundering herd on timeouts
                timeout = aiohttp.ClientTimeout(
                    total=HTTP_TIMEOUT + random.uniform(0, 5),
                    connect=10,
                    sock_read=HTTP_TIMEOUT
                )

                async with session.get(
                    url,
                    timeout=timeout,
                    headers=HTTP_HEADERS,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return (hour, data)
                    elif resp.status == 404:
                        # No data for this hour (holiday/weekend/empty) — normal
                        return (hour, b"")
                    elif resp.status in [500, 502, 503, 504]:
                        # Server error / Rate limited — back off aggressively
                        delay = min(
                            RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0.5, 2.0),
                            RETRY_MAX_DELAY
                        )
                        last_error = f"HTTP {resp.status}"
                        Logger.debug(f"Retrying {url} after {delay:.1f}s due to {last_error}")
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

        # All attempts exhausted
        if last_error and "503" in last_error:
            # Propagate backoff signal up the stack
            raise BackoffError(f"Repeated 503 errors for {url}")

        Logger.warning(f"Skipped {url.split('/datafeed/')[1]} after {DOWNLOAD_ATTEMPTS} retries ({last_error})")
        return (hour, b"")


async def fetch_day_async(symbol, day, semaphore):
    """
    Download all 24 hourly bi5 files for a given day.
    Staggers requests with small delays to avoid rate-limiting.
    Returns list of (hour, raw_bytes) tuples sorted by hour.
    """
    month_0indexed = day.month - 1

    # Optimize Connector
    connector = aiohttp.TCPConnector(
        limit=HOURLY_CONCURRENCY,
        limit_per_host=HOURLY_CONCURRENCY,
        force_close=False,        # Keep-Alive
        enable_cleanup_closed=True,
        ttl_dns_cache=300,        # Cache DNS for 5 minutes
        keepalive_timeout=30,     # Keep connection open for 30s
    )

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for hour in range(24):
            url = URL_TEMPLATE.format(
                currency=symbol,
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
    """
    if max_concurrent is None:
        max_concurrent = HOURLY_CONCURRENCY

    # Create a fresh loop for this thread if needed
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
             raise RuntimeError
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    semaphore = asyncio.Semaphore(max_concurrent)

    if loop.is_running():
         future = asyncio.run_coroutine_threadsafe(
             fetch_day_async(symbol, day, semaphore), loop
         )
         return future.result()
    else:
        return loop.run_until_complete(fetch_day_async(symbol, day, semaphore))
