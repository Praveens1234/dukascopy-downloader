"""
Dukascopy bi5 data processor.
Handles LZMA decompression, binary tick parsing, and price/volume normalization.
Pattern taken from duka repo's processor.py with per-hour timestamp fix.
"""

import struct
from datetime import datetime, timedelta
from lzma import LZMADecompressor, LZMAError, FORMAT_AUTO

from config.settings import DEFAULT_POINT_VALUE, VOLUME_MULTIPLIER, get_point_value
from utils.logger import get_logger

Logger = get_logger()


def decompress_lzma(data):
    """
    Decompress LZMA data handling multiple streams.
    bi5 files may contain multiple LZMA streams concatenated together.
    """
    if not data or len(data) == 0:
        return b""

    results = []
    while True:
        decomp = LZMADecompressor(FORMAT_AUTO, None, None)
        try:
            res = decomp.decompress(data)
        except LZMAError:
            if results:
                break  # Leftover data is not valid LZMA; ignore
            else:
                raise  # First iteration error; bail out
        results.append(res)
        data = decomp.unused_data
        if not data:
            break
        if not decomp.eof:
            raise LZMAError("Compressed data ended before end-of-stream marker")
    return b"".join(results)


def tokenize(buffer):
    """
    Parse decompressed binary data into raw tick tuples.
    Each tick is 20 bytes: !IIIff
      - I: time (ms offset from start of the hour)
      - I: ask price (integer, needs /point_value)
      - I: bid price (integer, needs /point_value)
      - f: ask volume (float, needs *VOLUME_MULTIPLIER)
      - f: bid volume (float, needs *VOLUME_MULTIPLIER)
    """
    token_size = 20
    count = len(buffer) // token_size
    tokens = []
    for i in range(count):
        tokens.append(
            struct.unpack('!IIIff', buffer[i * token_size: (i + 1) * token_size])
        )
    return tokens


def normalize_hour(symbol, day, hour, ticks):
    """
    Convert raw tick tuples for a specific hour to
    (datetime, ask, bid, ask_volume, bid_volume) tuples.
    time_ms is offset from start of the HOUR, not the day.
    """
    point = get_point_value(symbol)
    hour_start = datetime(day.year, day.month, day.day, hour, 0, 0)

    def norm(time_ms, ask_raw, bid_raw, ask_vol, bid_vol):
        dt = hour_start + timedelta(milliseconds=time_ms)
        return (
            dt,
            ask_raw / point,
            bid_raw / point,
            round(ask_vol * VOLUME_MULTIPLIER),
            round(bid_vol * VOLUME_MULTIPLIER),
        )

    normalized = [norm(*t) for t in ticks]
    # Layer 1: Drop ticks where both ask and bid are zero (server reset artefacts)
    return [t for t in normalized if t[1] > 0 or t[2] > 0]


def _filter_forward_filled_ticks(ticks):
    """
    Remove forward-filled synthetic ticks from sorted tick data.

    Dukascopy fills market closure periods (weekends, daily server resets,
    holidays) by repeating the last known tick values. Consecutive ticks
    with identical (ask, bid, ask_vol, bid_vol) are synthetic and must
    be removed to prevent fake candles in the output.

    Args:
        ticks: Sorted list of (datetime, ask, bid, ask_vol, bid_vol) tuples

    Returns:
        Filtered list with forward-filled ticks removed.
    """
    if not ticks:
        return ticks

    filtered = [ticks[0]]
    prev_vals = (ticks[0][1], ticks[0][2], ticks[0][3], ticks[0][4])

    for tick in ticks[1:]:
        vals = (tick[1], tick[2], tick[3], tick[4])
        if vals == prev_vals:
            continue  # Forward-filled duplicate — skip
        prev_vals = vals
        filtered.append(tick)

    return filtered


def decompress(symbol, day, hourly_data_list):
    """
    Full pipeline: for each (hour, compressed_bytes), decompress -> tokenize -> normalize.
    Returns combined list of (datetime, ask, bid, ask_volume, bid_volume) tuples,
    sorted chronologically, with forward-filled synthetic ticks removed.
    
    Args:
        symbol: Currency pair symbol
        day: date object
        hourly_data_list: list of (hour, compressed_bytes) tuples from fetch_day
    """
    all_ticks = []

    for hour, compressed_data in hourly_data_list:
        if compressed_data is None or len(compressed_data) == 0:
            continue
        try:
            raw = decompress_lzma(compressed_data)
            if len(raw) == 0:
                continue
            tokens = tokenize(raw)
            ticks = normalize_hour(symbol, day, hour, tokens)
            all_ticks.extend(ticks)
        except LZMAError as e:
            # Corrupted LZMA data for this hour — log and skip
            Logger.warning(f"LZMA decompression failed for {symbol} {day} hour {hour}: {e}")
        except struct.error as e:
            # Malformed binary data — log and skip
            Logger.warning(f"Binary parse error for {symbol} {day} hour {hour}: {e}")
        except Exception as e:
            # Unexpected error — log with full details instead of swallowing silently
            Logger.error(f"Unexpected error processing {symbol} {day} hour {hour}: {type(e).__name__}: {e}")

    # Sort by timestamp to ensure chronological order
    all_ticks.sort(key=lambda t: t[0])

    # Remove forward-filled synthetic ticks (market closure periods)
    all_ticks = _filter_forward_filled_ticks(all_ticks)

    return all_ticks
