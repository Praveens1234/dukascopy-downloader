"""
Dukascopy Historical Data Downloader - CLI Interface
Usage: python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1
"""

import sys
import os
import time
from datetime import datetime
from tqdm import tqdm

import click

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    TIMEFRAME_CHOICES, DEFAULT_THREADS, MAX_THREADS,
    DATA_SOURCE_CHOICES, PRICE_TYPE_CHOICES, VOLUME_TYPE_CHOICES,
)
from core.service import DownloaderService, DownloadConfig, ProgressObserver
from core.validator import validate_output, print_validation_report

class CLIProgressObserver(ProgressObserver):
    def __init__(self):
        self.pbar = None
        self.current_symbol = ""
        self.start_time = None

    def on_start(self, symbol: str, total_days: int):
        self.current_symbol = symbol
        self.start_time = time.time()
        print(f"\nProcessing {symbol} ({total_days} days)...")
        # Use simple progress bar for now, can be enhanced
        self.pbar = tqdm(total=total_days, unit="day", desc=symbol)

    def on_update(self, symbol: str, days_processed: int, total_days: int, success: bool):
        if self.pbar:
            # TQDM update is incremental, but here we get total processed.
            # So calculate delta
            current = self.pbar.n
            delta = days_processed - current
            if delta > 0:
                self.pbar.update(delta)

    def on_finish(self, symbol: str, output_path: str):
        if self.pbar:
            self.pbar.close()
            self.pbar = None

        elapsed = time.time() - self.start_time if self.start_time else 0
        print(f"  ✓ {symbol}: Written to {output_path} ({elapsed:.1f}s)")

        # Run validation
        # Extract dates from path or config?
        # Ideally validation logic should be part of service or triggered here.
        # Since service doesn't return validation results, we can trigger it here if we have date range.
        # But for now, let's keep it simple.

    def on_error(self, symbol: str, error: Exception):
        if self.pbar:
            self.pbar.close()
            self.pbar = None
        print(f"  ✗ {symbol} Error: {error}", file=sys.stderr)

    def log(self, message: str):
        # Avoid interfering with TQDM
        if self.pbar:
            self.pbar.write(f"  {message}")
        else:
            print(f"  {message}")


def validate_date(ctx, param, value):
    """Validate date string format."""
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        raise click.BadParameter(f"Invalid date format: '{value}'. Use YYYY-MM-DD")


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('symbols', nargs=-1, required=True)
@click.option(
    '-s', '--start', 'start_date',
    required=True,
    callback=validate_date,
    help='Start date (YYYY-MM-DD)',
)
@click.option(
    '-e', '--end', 'end_date',
    required=True,
    callback=validate_date,
    help='End date (YYYY-MM-DD)',
)
@click.option(
    '-t', '--timeframe',
    default='TICK',
    type=click.Choice(TIMEFRAME_CHOICES, case_sensitive=False),
    help='Data timeframe (default: TICK). Use CUSTOM with --custom-tf',
)
@click.option(
    '--custom-tf',
    'custom_tf',
    default=None,
    help='Custom timeframe: seconds (120), or suffixed (30s, 5m, 2h, 1d). Use with -t CUSTOM',
)
@click.option(
    '--threads',
    default=DEFAULT_THREADS,
    type=click.IntRange(1, MAX_THREADS),
    help=f'Number of parallel threads (default: {DEFAULT_THREADS})',
)
@click.option(
    '-o', '--output',
    default='.',
    type=click.Path(),
    help='Output directory (default: current directory)',
)
@click.option(
    '--header/--no-header',
    default=True,
    help='Include CSV header row (default: yes)',
)
@click.option(
    '--resume',
    is_flag=True,
    default=False,
    help='Resume a previously interrupted download',
)
@click.option(
    '--source',
    'data_source',
    default='auto',
    type=click.Choice(DATA_SOURCE_CHOICES, case_sensitive=False),
    help='Data source: auto, tick, or native (default: auto)',
)
@click.option(
    '--price-type',
    'price_type',
    default='BID',
    type=click.Choice(PRICE_TYPE_CHOICES, case_sensitive=False),
    help='Price type: BID, ASK, or MID (default: BID)',
)
@click.option(
    '--volume-type',
    'volume_type',
    default='TOTAL',
    type=click.Choice(VOLUME_TYPE_CHOICES, case_sensitive=False),
    help='Volume type: TOTAL, BID, ASK, or TICKS (default: TOTAL)',
)
def main(symbols, start_date, end_date, timeframe, custom_tf, threads,
         output, header, resume, data_source, price_type, volume_type):
    """
    Dukascopy Historical Data Downloader

    Download tick or candle data from Dukascopy's historical data feed.
    All timestamps are UTC. Output format: DD.MM.YYYY HH:MM:SS

    \b
    Examples:
      python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1
      python cli.py EURUSD -s 2024-01-01 -e 2024-01-02 -t S1
      python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 120
      python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 5m
      python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1 --source native --price-type BID
      python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t H1 --volume-type TICKS
      python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 --resume
    """
    if start_date > end_date:
        raise click.BadParameter("Start date must be before or equal to end date")

    if timeframe.upper() == 'CUSTOM' and not custom_tf:
        raise click.BadParameter("--custom-tf is required when using -t CUSTOM")

    # Convert symbols to uppercase
    symbols = [s.upper() for s in symbols]

    config = DownloadConfig(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date,
        timeframe=timeframe,
        threads=threads,
        data_source=data_source,
        price_type=price_type.upper(),
        volume_type=volume_type.upper(),
        custom_tf=custom_tf,
        output_dir=output,
        header=header,
        resume=resume
    )

    observer = CLIProgressObserver()
    service = DownloaderService(config, observer)

    try:
        print(f"\n{'=' * 60}")
        print(f"  Dukascopy Historical Data Downloader")
        print(f"{'=' * 60}")
        print(f"  Symbols:    {', '.join(symbols)}")
        print(f"  Date Range: {start_date} to {end_date}")
        print(f"  Threads:    {threads}")
        print(f"{'=' * 60}\n")

        service.run()

    except KeyboardInterrupt:
        service.cancel()
        print("\n\n  Download interrupted. Use --resume to continue later.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
