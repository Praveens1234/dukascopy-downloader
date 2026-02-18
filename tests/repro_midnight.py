import datetime
import os
import sys
import csv
from core.csv_dumper import CSVDumper
from config.settings import TimeFrame

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_midnight_bug():
    """
    Test to reproduce the 'Midnight Bug'.
    Demonstrates that aggregation resets daily, breaking multi-day candles.
    """
    print("Starting Midnight Bug Verification Test...")

    tf_seconds = 7 * 3600
    symbol = "TEST"
    start = datetime.date(2023, 1, 1)
    end = datetime.date(2023, 1, 2)
    folder = "tests/temp_midnight"
    os.makedirs(folder, exist_ok=True)

    dumper = CSVDumper(symbol, tf_seconds, start, end, folder)

    # Day 1 Data: 21:00 to 23:59
    day1 = datetime.date(2023, 1, 1)
    ticks_d1 = []
    base_d1 = datetime.datetime(2023, 1, 1, 21, 0, 0) # Start of the 21:00-04:00 candle
    for i in range(60): # 1 minute of ticks
        ticks_d1.append((base_d1 + datetime.timedelta(seconds=i), 1.0, 1.0, 1, 1))

    # Day 2 Data: 00:00 to 03:59
    day2 = datetime.date(2023, 1, 2)
    ticks_d2 = []
    base_d2 = datetime.datetime(2023, 1, 2, 0, 0, 0)
    for i in range(60): # 1 minute of ticks
        ticks_d2.append((base_d2 + datetime.timedelta(seconds=i), 1.0, 1.0, 1, 1))

    print(f"Appending Day 1 ticks ({len(ticks_d1)})...")
    dumper.append(day1, ticks_d1)

    print(f"Appending Day 2 ticks ({len(ticks_d2)})...")
    dumper.append(day2, ticks_d2)

    print("Dumping to CSV...")
    file_path = dumper.dump()
    print(f"Generated: {file_path}")

    # Read CSV
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"\nResulting CSV Rows: {len(rows)}")
    for r in rows:
        print(r)

    # Verification Logic
    # Should be 1 candle.
    # Volume should be 60 (Day 1) + 60 (Day 2) = 120
    # Wait, 60 ticks with 1 ask_vol + 1 bid_vol = 2 per tick?
    # CSVDumper defaults volume_type='TOTAL', so 1+1=2 per tick.
    # 60 ticks * 2 = 120 volume per day.
    # Total volume = 240.

    if len(rows) == 1:
        row = rows[0]
        vol = float(row['volume'])
        if vol == 240:
            print("\nPASS: Midnight bug fixed! 1 merged candle with correct volume.")
        else:
            print(f"\nFAIL: 1 candle found but volume is {vol} (expected 240).")
    else:
        print(f"\nFAIL: Expected 1 candle, found {len(rows)}.")

    # Cleanup
    import shutil
    if os.path.exists(folder):
        shutil.rmtree(folder)

if __name__ == "__main__":
    test_midnight_bug()
