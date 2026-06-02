"""
Data validator - Post-download checks for data integrity.
"""

from datetime import timedelta


def _parse_time(time_str):
    """Parse a time string, trying multiple formats.

    The CSV output uses DD.MM.YYYY HH:MM:SS[.mmm] format.
    This function handles that format as well as ISO format for robustness.
    """
    from datetime import datetime

    time_str = time_str.strip()

    # Try DD.MM.YYYY HH:MM:SS.mmm (our output format, with optional milliseconds)
    for fmt in ('%d.%m.%Y %H:%M:%S', '%d.%m.%Y %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue

    # Fallback: strip sub-second part and try DD.MM.YYYY HH:MM:SS
    base = time_str.split('.')[0]
    # But DD.MM.YYYY also starts with dots, so only strip if there's a space before the dot
    if ' ' in time_str:
        date_part, time_part = time_str.rsplit(' ', 1)
        # time_part might have .mmm at the end
        if '.' in time_part:
            time_part = time_part.split('.')[0]
        clean = f"{date_part} {time_part}"
        for fmt in ('%d.%m.%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S'):
            try:
                return datetime.strptime(clean, fmt)
            except ValueError:
                continue

    raise ValueError(f"Cannot parse time string: '{time_str}'")


def validate_output(file_path, start_date, end_date, symbol):
    """
    Validate the downloaded CSV data.
    Returns a dict with validation results.
    """
    import csv
    from datetime import datetime

    results = {
        'file': file_path,
        'symbol': symbol,
        'total_rows': 0,
        'issues': [],
        'valid': True,
    }

    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        results['total_rows'] = len(rows)

        if len(rows) == 0:
            results['issues'].append("File is empty - no data rows found")
            results['valid'] = False
            return results

        # Check for chronological ordering
        prev_time = None
        out_of_order = 0
        parse_errors = 0
        for row in rows:
            time_str = row.get('time', '')
            try:
                current_time = _parse_time(time_str)
                if prev_time and current_time < prev_time:
                    out_of_order += 1
                prev_time = current_time
            except (ValueError, TypeError):
                parse_errors += 1

        if out_of_order > 0:
            results['issues'].append(f"{out_of_order} rows are out of chronological order")

        if parse_errors > 0:
            results['issues'].append(f"{parse_errors} rows had unparseable timestamps")

        # Check price sanity (basic range check)
        if 'ask' in rows[0]:
            # Tick data
            prices = [float(r['ask']) for r in rows if r.get('ask')]
            if prices:
                min_p, max_p = min(prices), max(prices)
                if min_p <= 0:
                    results['issues'].append(f"Zero or negative prices found (min: {min_p})")
                results['price_range'] = f"{min_p:.5f} - {max_p:.5f}"
        elif 'open' in rows[0]:
            # Candle data
            prices = [float(r['open']) for r in rows if r.get('open')]
            if prices:
                min_p, max_p = min(prices), max(prices)
                if min_p <= 0:
                    results['issues'].append(f"Zero or negative prices found (min: {min_p})")
                results['price_range'] = f"{min_p:.5f} - {max_p:.5f}"

        if not results['issues']:
            results['issues'].append("No issues found")

    except Exception as e:
        results['issues'].append(f"Validation error: {str(e)}")
        results['valid'] = False

    return results


def print_validation_report(results):
    """Print a formatted validation report."""
    print(f"\n{'=' * 60}")
    print(f"  Validation Report: {results['symbol']}")
    print(f"{'=' * 60}")
    print(f"  File:       {results['file']}")
    print(f"  Total Rows: {results['total_rows']:,}")
    if 'price_range' in results:
        print(f"  Price Range: {results['price_range']}")
    print(f"  Status:     {'✓ VALID' if results['valid'] else '✗ ISSUES FOUND'}")
    for issue in results['issues']:
        prefix = "  ✓" if issue == "No issues found" else "  ⚠"
        print(f"{prefix} {issue}")
    print(f"{'=' * 60}\n")
