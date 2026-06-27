"""
Dukascopy Historical Data Downloader - Main Application
Orchestrates the download pipeline: fetch -> decompress -> aggregate -> dump.
Production-ready with anti-rate-limiting measures.
Supports native candle data and tick-to-candle conversion.
"""

import concurrent.futures
import os
import sys
import threading
import time
from collections import deque
from datetime import timedelta, date

# Force UTF-8 for Windows console output (needed for Unicode characters)
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, OSError):
        pass


from core.fetch import fetch_day
from core.processor import decompress
from core.csv_dumper import CSVDumper
from core.candle_fetch import fetch_native_candles
from core.validator import validate_output, print_validation_report
from config.settings import TimeFrame, SATURDAY, NATIVE_CANDLE_TIMEFRAMES, resolve_custom_timeframe
from utils.progress import DownloadProgress
from utils.resume import save_state, load_state, clear_state
from utils.logger import get_logger

Logger = get_logger(log_file='download.log')


def generate_days(start, end):
    """Generate trading days (skip Saturdays, skip today)."""
    if start > end:
        return
    current = start
    today = date.today()
    while current <= end:
        if current.weekday() != SATURDAY and current != today:
            yield current
        current += timedelta(days=1)


def count_days(start, end):
    """Count total trading days in range."""
    return sum(1 for _ in generate_days(start, end))


def _should_use_native(timeframe_str, data_source):
    """Determine if native candle data should be used."""
    tf_upper = timeframe_str.upper()
    if data_source == 'native':
        if tf_upper not in NATIVE_CANDLE_TIMEFRAMES:
            raise ValueError(
                f"Native candle data not available for {tf_upper}. "
                f"Only {', '.join(sorted(NATIVE_CANDLE_TIMEFRAMES))} are supported. "
                f"Use 'auto' or 'tick' data source instead."
            )
        return True
    elif data_source == 'auto':
        return tf_upper in NATIVE_CANDLE_TIMEFRAMES and tf_upper != 'TICK'
    return False  # data_source == 'tick'


def run_download(symbols, start, end, threads, timeframe, folder, header, resume,
                 data_source='auto', price_type='BID', volume_type='TOTAL',
                 custom_tf=None):
    """
    Main download orchestrator.
    Downloads tick data for all symbols in the date range,
    aggregates to the specified timeframe, and writes CSV output.

    Args:
        data_source: 'auto', 'tick', or 'native'
        price_type: 'BID', 'ASK', or 'MID'
        volume_type: 'TOTAL', 'BID', 'ASK', or 'TICKS'
        custom_tf: Custom timeframe string (e.g. '120', '30s', '2m')
    """
    os.makedirs(folder, exist_ok=True)

    # Resolve timeframe
    if timeframe.upper() == 'CUSTOM' and custom_tf:
        tf_value = resolve_custom_timeframe(custom_tf)
        tf_label = f"Custom ({tf_value}s)"
    else:
        tf_value = getattr(TimeFrame, timeframe.upper(), TimeFrame.TICK)
        tf_label = timeframe

    total_days = count_days(start, end)

    if total_days == 0:
        print("No trading days in the specified range.")
        return

    use_native = _should_use_native(timeframe, data_source)
    source_label = "Native Candle" if use_native else "Tick → Candle"

    all_days = list(generate_days(start, end))

    print(f"\n{'=' * 60}")
    print(f"  Dukascopy Historical Data Downloader")
    print(f"{'=' * 60}")
    print(f"  Symbols:    {', '.join(symbols)}")
    print(f"  Date Range: {start} to {end}")
    print(f"  Timeframe:  {tf_label}")
    print(f"  Source:     {source_label} | Price: {price_type} | Vol: {volume_type}")
    print(f"  Days:       {total_days}")
    print(f"  Threads:    {threads}")
    print(f"  Output:     {os.path.abspath(folder)}")
    print(f"{'=' * 60}\n")

    for symbol in symbols:
        if use_native:
            _download_symbol_native(
                symbol, start, end, timeframe, tf_value,
                folder, header, price_type, volume_type,
            )
        else:
            _download_symbol(
                symbol, start, end, all_days, total_days,
                threads, tf_value, folder, header, resume, price_type, volume_type,
            )


def _download_symbol_native(symbol, start, end, timeframe_str, tf_value,
                            folder, header, price_type, volume_type='TOTAL'):
    """Download data for a single symbol using native candle data."""
    print(f"  ⚡ {symbol}: Fetching native {timeframe_str} candles ({price_type})...")

    csv_dumper = CSVDumper(symbol, tf_value, start, end, folder, header, price_type, volume_type)

    # Split date range into yearly chunks (365 days max each)
    # Keeps memory flat (< 50MB peak RAM) and streams to disk chunk-by-chunk
    chunks = []
    curr_start = start
    while curr_start <= end:
        curr_end = min(curr_start + timedelta(days=364), end)
        chunks.append((curr_start, curr_end))
        curr_start = curr_end + timedelta(days=1)

    print(f"  ⚡ Processing native candles in {len(chunks)} yearly chunks...")

    total_candles = 0
    start_time = time.time()

    for idx, (chunk_start, chunk_end) in enumerate(chunks):
        print(f"  ⚡ Fetching chunk {idx+1}/{len(chunks)}: {chunk_start} to {chunk_end}...")
        try:
            candles = fetch_native_candles(symbol, chunk_start, chunk_end, timeframe_str.upper(), price_type)
            csv_dumper.append_native_candles(candles)
            csv_dumper.dump(append=True)
            total_candles += len(candles)
            print(f"  ✓ Chunk {idx+1}/{len(chunks)} saved successfully. ({len(candles):,} candles, RAM cleared)")
        except Exception as e:
            Logger.error(f"Native candle fetch failed for {symbol} chunk {idx+1}: {e}")
            print(f"  ✗ Chunk {idx+1}/{len(chunks)} failed — {str(e)[:60]}")

    elapsed = time.time() - start_time
    
    # Reconstruct exact safe file path that was written chunk-by-chunk
    safe_symbol = symbol.replace('/', '-')
    file_name = "{}-{}_{:02d}_{:02d}-{}_{:02d}_{:02d}.csv".format(
        safe_symbol,
        start.year, start.month, start.day,
        end.year, end.month, end.day,
    )
    import os
    file_path = os.path.join(folder, file_name)
    
    print(f"  ✓ {symbol}: All chunks written to {file_path} ({elapsed:.1f}s, Total candles: {total_candles:,})")

    # Validate
    results = validate_output(file_path, start, end, symbol)
    print_validation_report(results)


def _download_symbol(symbol, start, end, all_days, total_days,
                     threads, timeframe, folder, header, resume,
                     price_type='BID', volume_type='TOTAL'):
    """Download data for a single symbol using tick-to-candle conversion."""
    lock = threading.Lock()
    day_counter = [0]  # Use list for mutability in closure

    # Resume: skip already-completed dates
    if resume:
        completed_dates = load_state(folder, symbol)
        pending_days = [d for d in all_days if d not in completed_dates]
        already_done = len(all_days) - len(pending_days)
        if already_done > 0:
            print(f"  Resuming {symbol}: {already_done} days already downloaded, "
                  f"{len(pending_days)} remaining")
    else:
        completed_dates = set()
        pending_days = all_days

    if not pending_days:
        print(f"  {symbol}: All days already downloaded!")
        return

    progress = DownloadProgress(len(pending_days), symbol)
    csv_dumper = CSVDumper(symbol, timeframe, start, end, folder, header, price_type, volume_type)
    # Use a set for O(1) membership checks; convert to list only when saving
    completed_set = set(completed_dates)

    def do_work(day):
        """Download and process a single day."""
        try:
            raw_data = fetch_day(symbol, day)
            ticks = decompress(symbol, day, raw_data)
            with lock:
                csv_dumper.append(day, ticks)
                completed_set.add(day)
                day_counter[0] += 1
            progress.update(success=True)

            # Save state periodically for crash recovery
            if day_counter[0] % 20 == 0:
                with lock:
                    save_state(folder, symbol, list(completed_set), all_days)

        except Exception as e:
            Logger.error(f"Error processing {symbol} {day}: {e}")
            progress.update(success=False)

    # Run with thread pool — stagger submissions to avoid rate-limiting
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = []
        for i, day in enumerate(pending_days):
            futures.append(executor.submit(do_work, day))
            # Stagger thread submissions: small delay to prevent burst
            if i > 0 and i % threads == 0:
                time.sleep(0.5)

        for future in concurrent.futures.as_completed(futures):
            if future.exception() is not None:
                Logger.error(f"Thread error: {future.exception()}")

    progress.close()

    # Save state before CSV write (crash during write won't lose progress)
    if resume:
        save_state(folder, symbol, list(completed_set), all_days)

    # Write final CSV
    start_time = time.time()
    file_path = csv_dumper.dump()
    elapsed = time.time() - start_time
    print(f"  ✓ {symbol}: Written to {file_path} ({elapsed:.1f}s)")

    # Validate
    results = validate_output(file_path, start, end, symbol)
    print_validation_report(results)

    # Clear resume state on success
    clear_state(folder, symbol)
