"""
Dukascopy Native Candle Fetcher.
Downloads pre-computed OHLC candle data directly from Dukascopy's datafeed.

Supports: M1 (per-day), H1 (per-month), D1 (per-year).
Binary format: 24 bytes/candle as !IIIIIf
    (time_offset_sec, open, close, low, high, volume)
"""

import asyncio
import random
import struct
from datetime import datetime, date, timedelta
from calendar import monthrange
from lzma import LZMADecompressor, LZMAError, FORMAT_AUTO

import aiohttp

from config.settings import (
    CANDLE_URL_TEMPLATES, HTTP_HEADERS, HTTP_TIMEOUT,
    SPECIAL_POINT_SYMBOLS, DEFAULT_POINT_VALUE,
    DOWNLOAD_ATTEMPTS, RETRY_BASE_DELAY, RETRY_MAX_DELAY,
    REQUEST_DELAY, HOURLY_CONCURRENCY,
)
from utils.logger import get_logger

Logger = get_logger()

CANDLE_STRUCT = struct.Struct('!IIIIIf')  # 24 bytes
CANDLE_SIZE = CANDLE_STRUCT.size  # 24


def decompress_lzma(data):
    """Decompress LZMA data handling multiple streams."""
    if not data or len(data) == 0:
        return b""
    results = []
    while True:
        decomp = LZMADecompressor(FORMAT_AUTO, None, None)
        try:
            res = decomp.decompress(data)
        except LZMAError:
            if results:
                break
            else:
                raise
        results.append(res)
        data = decomp.unused_data
        if not data:
            break
        if not decomp.eof:
            break
    return b"".join(results)


def parse_candles(raw_data, base_time, symbol):
    """
    Parse decompressed candle binary data into OHLCV tuples.

    Binary format per candle (24 bytes, big-endian):
        uint32 time_offset  (seconds from base_time)
        uint32 open         (raw price, divide by point_value)
        uint32 close        (raw price)
        uint32 low          (raw price)
        uint32 high         (raw price)
        float32 volume

    Returns:
        List of (datetime, open, high, low, close, volume) tuples.
    """
    point = SPECIAL_POINT_SYMBOLS.get(symbol.lower(), DEFAULT_POINT_VALUE)
    candles = []
    count = len(raw_data) // CANDLE_SIZE

    for i in range(count):
        chunk = raw_data[i * CANDLE_SIZE: (i + 1) * CANDLE_SIZE]
        time_offset, raw_open, raw_close, raw_low, raw_high, volume = CANDLE_STRUCT.unpack(chunk)

        dt = base_time + timedelta(seconds=time_offset)
        o = raw_open / point
        h = raw_high / point
        l = raw_low / point
        c = raw_close / point
        v = round(volume, 2)

        candles.append((dt, o, h, l, c, v))

    return candles


async def _download_candle_file(session, url, semaphore):
    """Download a single candle .bi5 file with retries."""
    last_error = None
    async with semaphore:
        for attempt in range(DOWNLOAD_ATTEMPTS):
            try:
                async with session.get(
                    url,
                    headers=HTTP_HEADERS,
                    timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return data
                    elif resp.status == 404:
                        return b""  # No data for this period
                    elif resp.status == 503:
                        delay = min(
                            RETRY_BASE_DELAY * (2 ** attempt) + random.uniform(0.5, 2.0),
                            RETRY_MAX_DELAY
                        )
                        last_error = f"HTTP 503 (rate limited)"
                        await asyncio.sleep(delay)
                    else:
                        last_error = f"HTTP {resp.status}"
                        await asyncio.sleep(RETRY_BASE_DELAY)
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_error = str(e)
                await asyncio.sleep(RETRY_BASE_DELAY * (attempt + 1))

    Logger.warning(f"Failed to download candle file after {DOWNLOAD_ATTEMPTS} retries: {last_error}")
    return b""


def _build_m1_urls(symbol, start_date, end_date, price_type):
    """Build M1 candle URLs (one per day)."""
    template = CANDLE_URL_TEMPLATES['M1']
    urls = []
    current = start_date
    today = date.today()
    while current <= end_date:
        if current.weekday() != 5 and current != today:  # Skip Saturdays
            url = template.format(
                currency=symbol,
                year=current.year,
                month=current.month - 1,  # 0-indexed months
                day=current.day,
                price_type=price_type,
            )
            urls.append((current, url))
        current += timedelta(days=1)
    return urls


def _build_h1_urls(symbol, start_date, end_date, price_type):
    """Build H1 candle URLs (one per month)."""
    template = CANDLE_URL_TEMPLATES['H1']
    urls = []
    current = date(start_date.year, start_date.month, 1)
    end_month = date(end_date.year, end_date.month, 1)
    while current <= end_month:
        url = template.format(
            currency=symbol,
            year=current.year,
            month=current.month - 1,  # 0-indexed months
            price_type=price_type,
        )
        urls.append((current, url))
        # Move to next month
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return urls


def _build_d1_urls(symbol, start_date, end_date, price_type):
    """Build D1 candle URLs (one per year)."""
    template = CANDLE_URL_TEMPLATES['D1']
    urls = []
    for year in range(start_date.year, end_date.year + 1):
        url = template.format(
            currency=symbol,
            year=year,
            price_type=price_type,
        )
        urls.append((date(year, 1, 1), url))
    return urls


async def fetch_native_candles_async(symbol, start_date, end_date, timeframe_str, price_type='BID'):
    """
    Fetch native candle data from Dukascopy.

    Args:
        symbol: e.g. 'EURUSD'
        start_date: date object
        end_date: date object
        timeframe_str: 'M1', 'H1', or 'D1'
        price_type: 'BID' or 'ASK'

    Returns:
        List of (datetime, open, high, low, close, volume) tuples, filtered to date range.
    """
    if timeframe_str == 'M1':
        url_pairs = _build_m1_urls(symbol, start_date, end_date, price_type)
    elif timeframe_str == 'H1':
        url_pairs = _build_h1_urls(symbol, start_date, end_date, price_type)
    elif timeframe_str == 'D1':
        url_pairs = _build_d1_urls(symbol, start_date, end_date, price_type)
    else:
        raise ValueError(f"Native candles not available for timeframe: {timeframe_str}")

    all_candles = []
    semaphore = asyncio.Semaphore(HOURLY_CONCURRENCY)

    connector = aiohttp.TCPConnector(
        limit=HOURLY_CONCURRENCY,
        limit_per_host=HOURLY_CONCURRENCY,
        force_close=False,
        enable_cleanup_closed=True,
    )

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for base_date, url in url_pairs:
            tasks.append((base_date, url, _download_candle_file(session, url, semaphore)))
            if REQUEST_DELAY > 0:
                await asyncio.sleep(REQUEST_DELAY)

        # Gather results
        results = await asyncio.gather(*[t[2] for t in tasks], return_exceptions=True)

        for (base_date, url, _), compressed_data in zip(tasks, results):
            if isinstance(compressed_data, Exception):
                Logger.error(f"Error fetching {url}: {compressed_data}")
                continue
            if not compressed_data or len(compressed_data) == 0:
                continue

            try:
                raw = decompress_lzma(compressed_data)
                if len(raw) == 0:
                    continue

                # Base time depends on the timeframe level
                if timeframe_str == 'M1':
                    base_time = datetime(base_date.year, base_date.month, base_date.day, 0, 0, 0)
                elif timeframe_str == 'H1':
                    base_time = datetime(base_date.year, base_date.month, 1, 0, 0, 0)
                elif timeframe_str == 'D1':
                    base_time = datetime(base_date.year, 1, 1, 0, 0, 0)

                candles = parse_candles(raw, base_time, symbol)
                all_candles.extend(candles)
            except Exception as e:
                Logger.error(f"Error parsing candle data from {url}: {e}")

    # Filter to requested date range and sort
    start_dt = datetime(start_date.year, start_date.month, start_date.day)
    end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
    all_candles = [c for c in all_candles if start_dt <= c[0] <= end_dt]
    all_candles.sort(key=lambda c: c[0])

    return all_candles


def fetch_native_candles(symbol, start_date, end_date, timeframe_str, price_type='BID'):
    """Synchronous wrapper for native candle fetching."""
    return asyncio.run(fetch_native_candles_async(symbol, start_date, end_date, timeframe_str, price_type))
