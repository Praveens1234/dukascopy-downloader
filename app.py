"""
Dukascopy Historical Data Downloader - Main Application
Orchestrates the download pipeline: fetch -> decompress -> aggregate -> dump.
Production-ready with anti-rate-limiting measures.
"""

import concurrent.futures
import os
import threading
import time
from collections import deque
from datetime import timedelta, date

from core.fetch import fetch_day
from core.processor import decompress
from core.csv_dumper import CSVDumper
from core.validator import validate_output, print_validation_report
from config.settings import TimeFrame, SATURDAY
from utils.progress import DownloadProgress
from utils.resume import save_state, load_state, clear_state
from utils.logger import get_logger

Logger = get_logger()


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


def run_download(symbols, start, end, threads, timeframe, folder, header, resume):
    """
    Main download orchestrator.
    Downloads tick data for all symbols in the date range,
    aggregates to the specified timeframe, and writes CSV output.
    """
    os.makedirs(folder, exist_ok=True)

    tf_value = getattr(TimeFrame, timeframe.upper(), TimeFrame.TICK)
    total_days = count_days(start, end)

    if total_days == 0:
        print("No trading days in the specified range.")
        return

    all_days = list(generate_days(start, end))

    print(f"\n{'=' * 60}")
    print(f"  Dukascopy Historical Data Downloader")
    print(f"{'=' * 60}")
    print(f"  Symbols:    {', '.join(symbols)}")
    print(f"  Date Range: {start} to {end}")
    print(f"  Timeframe:  {timeframe}")
    print(f"  Days:       {total_days}")
    print(f"  Threads:    {threads}")
    print(f"  Output:     {os.path.abspath(folder)}")
    print(f"{'=' * 60}\n")

    for symbol in symbols:
        _download_symbol(
            symbol, start, end, all_days, total_days,
            threads, tf_value, folder, header, resume,
        )


def _download_symbol(symbol, start, end, all_days, total_days,
                     threads, timeframe, folder, header, resume):
    """Download data for a single symbol."""
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
    csv_dumper = CSVDumper(symbol, timeframe, start, end, folder, header)
    completed_list = list(completed_dates)

    def do_work(day):
        """Download and process a single day."""
        try:
            raw_data = fetch_day(symbol, day)
            ticks = decompress(symbol, day, raw_data)
            with lock:
                csv_dumper.append(day, ticks)
                completed_list.append(day)
                day_counter[0] += 1
            progress.update(success=True)

            # Save state frequently for crash recovery
            if day_counter[0] % 5 == 0:
                with lock:
                    save_state(folder, symbol, completed_list, all_days)

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
