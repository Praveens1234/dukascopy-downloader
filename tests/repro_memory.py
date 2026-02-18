import os
import sys
import tracemalloc
import datetime
import gc
from core.csv_dumper import CSVDumper
from config.settings import TimeFrame

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_memory_leak():
    """
    Test to demonstrate that CSVDumper buffers everything in memory.
    """
    print("Starting Memory Leak Reproduction Test...")

    # Setup Dumper
    symbol = "TEST"
    timeframe = TimeFrame.TICK
    start = datetime.date(2023, 1, 1)
    end = datetime.date(2023, 1, 2)
    folder = "tests/temp_output"
    os.makedirs(folder, exist_ok=True)

    dumper = CSVDumper(symbol, timeframe, start, end, folder)

    print("Generating 1,000,000 mock ticks...")
    ticks = []
    base_time = datetime.datetime(2023, 1, 1, 0, 0, 0)
    for i in range(1_000_000):
        t = (base_time + datetime.timedelta(milliseconds=i), 1.0500, 1.0499, 1.5, 1.2)
        ticks.append(t)

    print("Taking snapshot BEFORE append...")
    gc.collect()
    tracemalloc.start()
    start_snapshot = tracemalloc.take_snapshot()

    print("Appending to Dumper...")
    dumper.append(start, ticks)

    print("Taking snapshot AFTER append...")
    gc.collect()
    end_snapshot = tracemalloc.take_snapshot()

    stats = end_snapshot.compare_to(start_snapshot, 'lineno')

    print("\nTop 10 Memory Blocks Growth:")
    for stat in stats[:10]:
        print(stat)

    total_size = sum(stat.size for stat in stats)
    total_mb = total_size / 1024 / 1024
    print(f"\nTotal Memory Growth due to Dumper: {total_mb:.2f} MB")

    # cleanup
    try:
        import shutil
        shutil.rmtree(folder)
    except:
        pass

    if total_mb > 50:
        print("FAIL: Significant memory retention detected.")
    else:
        print("PASS: Memory usage low (Streaming verified).")

if __name__ == "__main__":
    test_memory_leak()
