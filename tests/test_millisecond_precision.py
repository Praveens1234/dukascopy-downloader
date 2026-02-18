import requests
import time
import os
import sys
import csv

BASE_URL = "http://localhost:8000"

def test_tick_precision():
    print("1. Testing TICK Download (Millisecond Precision)...")
    
    # Clean prev output
    expected_file = os.path.join("data", "EURUSD-2024_01_15-2024_01_15.csv")
    if os.path.exists(expected_file):
        os.remove(expected_file)
        
    payload = {
        "symbols": ["EURUSD"],
        "start_date": "2024-01-15",
        "end_date": "2024-01-15",
        "timeframe": "TICK",
        "threads": 5,
        "data_source": "tick", # Force tick
        "price_type": "BID",
        "volume_type": "TICKS"
    }
    
    try:
        res = requests.post(f"{BASE_URL}/api/download", json=payload)
        res.raise_for_status()
        data = res.json()
        job_id = data["job_id"]
        print(f"   ✅ Job started. ID: {job_id}")
    except Exception as e:
        print(f"   ❌ Download request failed: {e}")
        try: print(res.text)
        except: pass
        sys.exit(1)

    # Poll API
    for _ in range(60):
        try:
            r = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
            if r.status_code == 200:
                j = r.json()
                status = j.get("status")
                if status == "completed":
                    print("   ✅ Job completed!")
                    break
                elif status == "failed":
                    print(f"   ❌ Job failed: {j.get('error')}")
                    sys.exit(1)
        except: pass
        time.sleep(1)
    else:
        print("   ❌ Timeout waiting for job.")
        sys.exit(1)
        
    # Verify file content
    if not os.path.exists(expected_file):
        print(f"   ❌ File missing: {expected_file}")
        sys.exit(1)
        
    print(f"   ℹ Checking timestamps in {expected_file}...")
    with open(expected_file, 'r', newline='') as f:
        reader = csv.DictReader(f)
        row1 = next(reader)
        ts = row1['time']
        print(f"   First timestamp: {ts}")
        
        # Check format: DD.MM.YYYY HH:MM:SS.mmm
        # Regex or simple check
        if '.' in ts.split(' ')[1]: # Check for dot in time part
            print("   ✅ Milliseconds present!")
        else:
            print("   ⚠ Warning: No milliseconds in first row. Checking more rows...")
            found = False
            for i, row in enumerate(reader):
                if i > 100: break
                if '.' in row['time'].split(' ')[1]:
                    print(f"   ✅ Found milliseconds at row {i+2}: {row['time']}")
                    found = True
                    break
            if not found:
                print("   ❌ No milliseconds found in first 100 rows!")
                sys.exit(1)
    
if __name__ == "__main__":
    test_tick_precision()
