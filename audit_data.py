"""
XAUUSD 1M Data Audit Script
Checks for: zero values, time gaps, price anomalies, and data completeness.
Classifies gaps as Expected (weekend/daily-reset/holiday) or Unexpected.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# XAUUSD trading hours: Sunday 22:00 UTC to Friday 22:00 UTC (approx)
# Daily server reset gap: ~21:00-22:00 UTC (varies slightly)

KNOWN_HOLIDAYS_2025_2026 = {
    # (month, day): description - US/Global market holidays affecting Gold
    (1, 1): "New Year's Day",
    (1, 20): "MLK Day (2025)",
    (2, 17): "Presidents' Day (2025)",
    (4, 18): "Good Friday (2025)",
    (5, 26): "Memorial Day (2025)",
    (7, 4): "Independence Day",
    (9, 1): "Labor Day (2025)",
    (11, 27): "Thanksgiving (2025)",
    (12, 25): "Christmas Day",
    (12, 26): "Boxing Day (some markets)",
    (1, 19): "MLK Day (2026)",
    (2, 16): "Presidents' Day (2026)",
}


def audit_csv(file_path):
    print(f"\n{'='*70}")
    print(f"  XAUUSD 1-MINUTE DATA AUDIT REPORT")
    print(f"{'='*70}")
    print(f"  File: {file_path}")

    # Load CSV
    df = pd.read_csv(file_path)
    
    # Detect datetime format
    sample = df.iloc[0]['datetime'] if 'datetime' in df.columns else df.iloc[0][df.columns[0]]
    time_col = 'datetime' if 'datetime' in df.columns else df.columns[0]
    
    # Try multiple date formats
    for fmt in ['%d.%m.%Y %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%d.%m.%Y %H:%M']:
        try:
            df['time_parsed'] = pd.to_datetime(df[time_col], format=fmt)
            break
        except:
            continue
    else:
        df['time_parsed'] = pd.to_datetime(df[time_col])
    
    df = df.sort_values('time_parsed').reset_index(drop=True)
    
    # Identify price columns
    price_cols = []
    for col in ['open', 'high', 'low', 'close']:
        if col in df.columns:
            price_cols.append(col)
    
    vol_col = 'volume' if 'volume' in df.columns else None

    print(f"  Total Rows: {len(df):,}")
    print(f"  Date Range: {df['time_parsed'].min()} → {df['time_parsed'].max()}")
    total_calendar_days = (df['time_parsed'].max() - df['time_parsed'].min()).days
    print(f"  Calendar Days Covered: {total_calendar_days}")
    print(f"  Columns: {list(df.columns)}")
    print(f"{'='*70}\n")

    # =========================================================================
    # 1. ZERO VALUES CHECK
    # =========================================================================
    print(f"{'─'*70}")
    print(f"  1. ZERO VALUES CHECK")
    print(f"{'─'*70}")
    
    zero_count = 0
    for col in price_cols:
        zeros = df[df[col] == 0]
        if len(zeros) > 0:
            zero_count += len(zeros)
            print(f"  ✗ {col}: {len(zeros)} zero values found")
            print(f"    First 5 occurrences:")
            for _, row in zeros.head(5).iterrows():
                print(f"      {row['time_parsed']}: {col}={row[col]}")
    
    if zero_count == 0:
        print(f"  ✓ PASS - No zero prices found in any OHLC column")
    else:
        print(f"\n  ✗ FAIL - Total {zero_count} zero values detected")
    
    # =========================================================================
    # 2. NEGATIVE / NaN VALUES CHECK
    # =========================================================================
    print(f"\n{'─'*70}")
    print(f"  2. NEGATIVE / NaN / INVALID VALUES CHECK")
    print(f"{'─'*70}")
    
    issues = 0
    for col in price_cols:
        nan_count = df[col].isna().sum()
        neg_count = (df[col] < 0).sum()
        if nan_count > 0:
            print(f"  ✗ {col}: {nan_count} NaN values")
            issues += nan_count
        if neg_count > 0:
            print(f"  ✗ {col}: {neg_count} negative values")
            issues += neg_count
    
    if issues == 0:
        print(f"  ✓ PASS - No NaN or negative values found")

    # =========================================================================
    # 3. OHLC LOGIC CHECK
    # =========================================================================
    print(f"\n{'─'*70}")
    print(f"  3. OHLC LOGIC CHECK (High >= Low, High >= Open/Close)")
    print(f"{'─'*70}")
    
    if all(c in df.columns for c in ['open', 'high', 'low', 'close']):
        bad_hl = df[df['high'] < df['low']]
        bad_ho = df[df['high'] < df['open']]
        bad_hc = df[df['high'] < df['close']]
        bad_lo = df[df['low'] > df['open']]
        bad_lc = df[df['low'] > df['close']]
        
        total_bad = len(bad_hl) + len(bad_ho) + len(bad_hc) + len(bad_lo) + len(bad_lc)
        
        if total_bad == 0:
            print(f"  ✓ PASS - All {len(df):,} candles have valid OHLC relationships")
        else:
            if len(bad_hl) > 0:
                print(f"  ✗ High < Low: {len(bad_hl)} occurrences")
            if len(bad_ho) > 0:
                print(f"  ✗ High < Open: {len(bad_ho)} occurrences")
            if len(bad_hc) > 0:
                print(f"  ✗ High < Close: {len(bad_hc)} occurrences")
            if len(bad_lo) > 0:
                print(f"  ✗ Low > Open: {len(bad_lo)} occurrences")
            if len(bad_lc) > 0:
                print(f"  ✗ Low > Close: {len(bad_lc)} occurrences")

    # =========================================================================
    # 4. TIME GAP ANALYSIS (CORE AUDIT)
    # =========================================================================
    print(f"\n{'─'*70}")
    print(f"  4. TIME GAP ANALYSIS")
    print(f"{'─'*70}")
    
    df['gap_minutes'] = df['time_parsed'].diff().dt.total_seconds() / 60.0
    
    # Gaps > 1 minute
    gaps = df[df['gap_minutes'] > 1.0].copy()
    print(f"  Total gaps (> 1 min): {len(gaps)}")
    
    # Classify each gap
    weekend_gaps = []
    daily_reset_gaps = []
    holiday_gaps = []
    unexpected_gaps = []
    
    for idx, row in gaps.iterrows():
        gap_end = row['time_parsed']
        gap_start = gap_end - timedelta(minutes=row['gap_minutes'])
        gap_min = row['gap_minutes']
        
        # Weekend check: Friday ~22:00 to Sunday ~22:00 (about 2880 min = 48h)
        # Or Friday to Sunday/Monday
        start_wd = gap_start.weekday()  # 0=Mon, 4=Fri, 5=Sat, 6=Sun
        end_wd = gap_end.weekday()
        
        is_weekend = False
        # Classic weekend: starts Fri evening, ends Sun evening/Mon
        if start_wd == 4 and gap_min >= 1400:  # Fri, gap > ~23h
            is_weekend = True
        elif start_wd == 4 and end_wd in [6, 0] and gap_min >= 600:
            is_weekend = True
        elif start_wd == 5:  # Sat
            is_weekend = True
            
        # Daily server reset: typically 1-65 min gap around 21:00-23:00 UTC
        is_daily_reset = (
            gap_min <= 65 
            and gap_start.hour in [20, 21, 22] 
            and not is_weekend
        )
        
        # Holiday check
        is_holiday = False
        check_date = gap_start.date()
        for d_offset in range(int(gap_min // 1440) + 2):
            check = check_date + timedelta(days=d_offset)
            if (check.month, check.day) in KNOWN_HOLIDAYS_2025_2026:
                is_holiday = True
                break
        
        entry = {
            'gap_start': gap_start,
            'gap_end': gap_end,
            'gap_minutes': gap_min,
            'gap_hours': round(gap_min / 60, 1),
        }
        
        if is_weekend:
            weekend_gaps.append(entry)
        elif is_daily_reset:
            daily_reset_gaps.append(entry)
        elif is_holiday:
            holiday_gaps.append(entry)
        else:
            unexpected_gaps.append(entry)
    
    print(f"\n  Gap Classification:")
    print(f"  ├── Weekend Gaps:     {len(weekend_gaps):>4}  (Expected)")
    print(f"  ├── Daily Reset Gaps: {len(daily_reset_gaps):>4}  (Expected)")
    print(f"  ├── Holiday Gaps:     {len(holiday_gaps):>4}  (Expected)")
    print(f"  └── Unexpected Gaps:  {len(unexpected_gaps):>4}  {'✗ NEEDS REVIEW' if unexpected_gaps else '✓ NONE'}")
    
    # Weekend gap details
    if weekend_gaps:
        print(f"\n  Weekend Gaps (sample):")
        for g in weekend_gaps[:5]:
            print(f"    {g['gap_start']} → {g['gap_end']} ({g['gap_hours']}h)")
    
    # Daily reset details
    if daily_reset_gaps:
        reset_durations = [g['gap_minutes'] for g in daily_reset_gaps]
        print(f"\n  Daily Reset Gaps:")
        print(f"    Count: {len(daily_reset_gaps)}")
        print(f"    Min: {min(reset_durations):.0f} min, Max: {max(reset_durations):.0f} min, Avg: {np.mean(reset_durations):.1f} min")
    
    # Holiday gap details
    if holiday_gaps:
        print(f"\n  Holiday Gaps:")
        for g in holiday_gaps:
            print(f"    {g['gap_start']} → {g['gap_end']} ({g['gap_hours']}h)")
    
    # UNEXPECTED gaps — the critical ones
    if unexpected_gaps:
        print(f"\n  ⚠️  UNEXPECTED GAPS (Require Investigation):")
        print(f"  {'Start':<22} {'End':<22} {'Duration':>10} {'Notes'}")
        print(f"  {'─'*66}")
        for g in unexpected_gaps[:30]:
            dur = f"{g['gap_hours']}h" if g['gap_hours'] >= 1 else f"{g['gap_minutes']:.0f}m"
            day_name = g['gap_start'].strftime('%A')
            print(f"  {str(g['gap_start']):<22} {str(g['gap_end']):<22} {dur:>10} {day_name}")
        
        if len(unexpected_gaps) > 30:
            print(f"  ... and {len(unexpected_gaps) - 30} more")
    
    # =========================================================================
    # 5. DATA COMPLETENESS
    # =========================================================================
    print(f"\n{'─'*70}")
    print(f"  5. DATA COMPLETENESS")
    print(f"{'─'*70}")
    
    # Expected: ~5 trading days/week, ~22h/day, ~60 min/hour = ~6600 min/week
    # For 14 months (~60 weeks) ≈ ~396,000 minutes
    expected_trading_weeks = total_calendar_days / 7
    expected_minutes = expected_trading_weeks * 5 * 22 * 60  # rough estimate
    completeness = (len(df) / expected_minutes) * 100 if expected_minutes > 0 else 0
    
    print(f"  Actual Data Points:   {len(df):>10,}")
    print(f"  Expected (est.):      {int(expected_minutes):>10,}")
    print(f"  Completeness:         {completeness:>9.1f}%")
    
    # Monthly breakdown
    df['month'] = df['time_parsed'].dt.to_period('M')
    monthly = df.groupby('month').agg(
        count=('time_parsed', 'count'),
        min_price=(price_cols[2] if len(price_cols) > 2 else price_cols[0], 'min'),  # low
        max_price=(price_cols[1] if len(price_cols) > 1 else price_cols[0], 'max'),  # high
    )
    
    print(f"\n  Monthly Data Distribution:")
    print(f"  {'Month':<12} {'Candles':>10} {'Low':>12} {'High':>12}")
    print(f"  {'─'*48}")
    for period, row in monthly.iterrows():
        print(f"  {str(period):<12} {row['count']:>10,} {row['min_price']:>12,.3f} {row['max_price']:>12,.3f}")

    # =========================================================================
    # 6. PRICE SPIKE / ANOMALY CHECK
    # =========================================================================
    print(f"\n{'─'*70}")
    print(f"  6. PRICE SPIKE / ANOMALY CHECK")
    print(f"{'─'*70}")
    
    if 'close' in df.columns:
        df['pct_change'] = df['close'].pct_change().abs() * 100
        spikes = df[df['pct_change'] > 2.0]  # > 2% move in 1 minute
        
        if len(spikes) > 0:
            print(f"  ⚠️  {len(spikes)} candles with > 2% price change in 1 minute:")
            for _, row in spikes.head(10).iterrows():
                print(f"    {row['time_parsed']}: {row['pct_change']:.2f}% change (close={row['close']:.3f})")
            if len(spikes) > 10:
                print(f"    ... and {len(spikes) - 10} more")
        else:
            print(f"  ✓ PASS - No extreme price spikes (> 2% per minute)")

    # =========================================================================
    # 7. VOLUME CHECK
    # =========================================================================
    print(f"\n{'─'*70}")
    print(f"  7. VOLUME CHECK")
    print(f"{'─'*70}")
    
    if vol_col and vol_col in df.columns:
        zero_vol = df[df[vol_col] == 0]
        neg_vol = df[df[vol_col] < 0]
        print(f"  Zero volume candles: {len(zero_vol)}")
        print(f"  Negative volume:     {len(neg_vol)}")
        print(f"  Min volume:          {df[vol_col].min():,.0f}")
        print(f"  Max volume:          {df[vol_col].max():,.0f}")
        print(f"  Avg volume:          {df[vol_col].mean():,.0f}")
        
        if len(zero_vol) == 0 and len(neg_vol) == 0:
            print(f"  ✓ PASS")
        else:
            print(f"  ⚠️  {len(zero_vol)} zero-volume candles found")

    # =========================================================================
    # 8. DUPLICATE CHECK
    # =========================================================================
    print(f"\n{'─'*70}")
    print(f"  8. DUPLICATE TIMESTAMP CHECK")
    print(f"{'─'*70}")
    
    dupes = df[df.duplicated(subset=['time_parsed'], keep=False)]
    if len(dupes) > 0:
        print(f"  ✗ FAIL - {len(dupes)} duplicate timestamps found")
        print(f"  First 5 duplicates:")
        for _, row in dupes.head(10).iterrows():
            print(f"    {row['time_parsed']}")
    else:
        print(f"  ✓ PASS - No duplicate timestamps")

    # =========================================================================
    # FINAL VERDICT
    # =========================================================================
    print(f"\n{'='*70}")
    print(f"  FINAL VERDICT")
    print(f"{'='*70}")
    
    all_pass = (
        zero_count == 0
        and issues == 0
        and len(unexpected_gaps) == 0
    )
    
    if all_pass:
        print(f"  ✓ DATA QUALITY: EXCELLENT")
        print(f"    No zero prices, no unexpected gaps, valid OHLC logic.")
    elif zero_count == 0 and len(unexpected_gaps) <= 10:
        print(f"  ⚠️  DATA QUALITY: GOOD (minor issues)")
        print(f"    {len(unexpected_gaps)} unexpected gaps found — may be low-liquidity periods.")
    else:
        print(f"  ✗ DATA QUALITY: NEEDS ATTENTION")
        if zero_count > 0:
            print(f"    - {zero_count} zero price entries")
        if len(unexpected_gaps) > 0:
            print(f"    - {len(unexpected_gaps)} unexpected gaps")
    
    print(f"{'='*70}\n")
    
    return {
        'zero_count': zero_count,
        'unexpected_gaps': len(unexpected_gaps),
        'total_rows': len(df),
        'completeness': completeness,
    }


if __name__ == "__main__":
    if len(sys.argv) > 1:
        audit_csv(sys.argv[1])
    else:
        target = r"C:\Users\prave\Downloads\XAUUSD\XAUUSD-2025_01_01-2026_02_11.csv"
        if os.path.exists(target):
            audit_csv(target)
        else:
            print("Usage: python audit_data.py <path_to_csv>")
