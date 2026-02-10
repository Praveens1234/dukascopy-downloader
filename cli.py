"""
Dukascopy Historical Data Downloader - CLI Interface
Usage: python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1
"""

import sys
import os
from datetime import datetime

import click

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import TIMEFRAME_CHOICES, DEFAULT_THREADS, MAX_THREADS
from app import run_download


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
    help='Data timeframe (default: TICK)',
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
def main(symbols, start_date, end_date, timeframe, threads, output, header, resume):
    """
    Dukascopy Historical Data Downloader

    Download tick or candle data from Dukascopy's historical data feed.

    \b
    Examples:
      python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1
      python cli.py EURUSD GBPUSD -s 2024-01-01 -e 2024-06-30 -t TICK
      python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t H1 --threads 20
      python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 --resume
    """
    if start_date > end_date:
        raise click.BadParameter("Start date must be before or equal to end date")

    # Convert symbols to uppercase
    symbols = [s.upper() for s in symbols]

    try:
        run_download(
            symbols=symbols,
            start=start_date,
            end=end_date,
            threads=threads,
            timeframe=timeframe,
            folder=output,
            header=header,
            resume=resume,
        )
    except KeyboardInterrupt:
        print("\n\n  Download interrupted. Use --resume to continue later.")
        sys.exit(1)
    except Exception as e:
        print(f"\n  Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
