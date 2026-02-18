"""
Data validator - Post-download checks for data integrity.
Optimized for streaming large files without loading into memory.
"""

import csv
import sys
from datetime import datetime, timedelta

# Default format in output CSV
DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

def validate_output(file_path, start_date, end_date, symbol):
    """
    Validate the downloaded CSV data with strict checks.
    Stream-processes the file to avoid memory issues.
    """
    results = {
        'file': file_path,
        'symbol': symbol,
        'total_rows': 0,
        'issues': [],
        'valid': True,
        'price_range': "N/A",
        'date_range': "N/A",
    }

    try:
        prev_time = None
        min_p = float('inf')
        max_p = float('-inf')
        out_of_order_count = 0
        duplicate_count = 0
        bad_ohlc_count = 0
        zero_price_count = 0
        max_gap = timedelta(0)

        is_candle = False
        row_count = 0

        with open(file_path, 'r') as f:
            # Check header
            header_line = f.readline()
            f.seek(0)

            if not header_line:
                results['issues'].append("File is empty")
                results['valid'] = False
                return results

            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames

            if 'open' in fieldnames:
                is_candle = True
            elif 'ask' in fieldnames:
                is_candle = False
            else:
                results['issues'].append(f"Unknown CSV format: {fieldnames}")
                results['valid'] = False
                return results

            first_dt = None
            last_dt = None

            for row in reader:
                row_count += 1

                # Time Parsing
                time_str = row.get('time', '')
                try:
                    # Split '.' just in case ms are present, though format is usually clean
                    current_time = datetime.strptime(time_str, DATETIME_FORMAT)
                except ValueError:
                     # Attempt fallback if format differs
                     try:
                         current_time = datetime.strptime(time_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                     except:
                         results['issues'].append(f"Invalid date format at row {row_count}: {time_str}")
                         if len(results['issues']) > 10: break
                         continue

                if first_dt is None:
                    first_dt = current_time
                last_dt = current_time

                # Chronological Check
                if prev_time:
                    if current_time < prev_time:
                        out_of_order_count += 1
                    elif current_time == prev_time:
                        duplicate_count += 1
                    else:
                        gap = current_time - prev_time
                        if gap > max_gap:
                            max_gap = gap

                prev_time = current_time

                # Price Checks
                try:
                    if is_candle:
                        o = float(row['open'])
                        h = float(row['high'])
                        l = float(row['low'])
                        c = float(row['close'])

                        min_p = min(min_p, l)
                        max_p = max(max_p, h)

                        if min(o, h, l, c) <= 0:
                            zero_price_count += 1

                        # OHLC Logic
                        if not (h >= o and h >= c and h >= l and l <= o and l <= c):
                            bad_ohlc_count += 1

                    else:
                        # Tick
                        a = float(row['ask'])
                        b = float(row['bid'])

                        min_p = min(min_p, b) # Bid is usually lower
                        max_p = max(max_p, a)

                        if a <= 0 or b <= 0:
                            zero_price_count += 1

                except ValueError:
                    results['issues'].append(f"Non-numeric price at row {row_count}")

        results['total_rows'] = row_count

        if first_dt and last_dt:
            results['date_range'] = f"{first_dt} -> {last_dt}"

        if min_p != float('inf'):
            results['price_range'] = f"{min_p:.5f} - {max_p:.5f}"

        # Consolidate issues
        if out_of_order_count > 0:
            results['issues'].append(f"{out_of_order_count} rows out of order")
            results['valid'] = False

        if duplicate_count > 0:
            # Duplicates might be okay for ticks (same ms), but suspicious for candles
            msg = f"{duplicate_count} duplicate timestamps"
            if is_candle:
                results['issues'].append(msg + " (Critical for Candles)")
                results['valid'] = False
            else:
                # Info only for ticks
                # actually duplicate ticks are fine if volume/price differs?
                # But strict chronological check usually implies unique index for candles.
                pass

        if zero_price_count > 0:
            results['issues'].append(f"{zero_price_count} rows with zero/negative prices")
            results['valid'] = False

        if bad_ohlc_count > 0:
            results['issues'].append(f"{bad_ohlc_count} rows with invalid OHLC (High < Low etc.)")
            results['valid'] = False

        if row_count == 0:
            results['issues'].append("File is empty")
            results['valid'] = False

        if max_gap.total_seconds() > 0:
             # Just info
             pass

        if not results['issues']:
            results['issues'].append("No issues found")

    except Exception as e:
        results['issues'].append(f"Validation fatal error: {str(e)}")
        results['valid'] = False

    return results


def print_validation_report(results):
    """Print a formatted validation report."""
    print(f"\n{'=' * 60}")
    print(f"  Validation Report: {results['symbol']}")
    print(f"{'=' * 60}")
    print(f"  File:       {results['file']}")
    print(f"  Total Rows: {results['total_rows']:,}")
    if results['date_range'] != "N/A":
        print(f"  Date Range: {results['date_range']}")
    if results['price_range'] != "N/A":
        print(f"  Price Range: {results['price_range']}")

    print(f"  Status:     {'✓ VALID' if results['valid'] else '✗ ISSUES FOUND'}")

    for issue in results['issues']:
        if issue == "No issues found":
            print(f"  ✓ {issue}")
        else:
            print(f"  ⚠ {issue}")

    print(f"{'=' * 60}\n")
