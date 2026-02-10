"""
Data validator - Post-download checks for data integrity.
"""

from datetime import timedelta


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
        for row in rows:
            time_str = row.get('time', '')
            try:
                current_time = datetime.strptime(time_str.split('.')[0], '%Y-%m-%d %H:%M:%S')
                if prev_time and current_time < prev_time:
                    out_of_order += 1
                prev_time = current_time
            except ValueError:
                pass

        if out_of_order > 0:
            results['issues'].append(f"{out_of_order} rows are out of chronological order")

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
