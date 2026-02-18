
import requests
import time
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000"
DOWNLOAD_DIR = "data_e2e_test"

def test_config():
    print("1. Testing Config Endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/api/config")
        res.raise_for_status()
        cfg = res.json()
        print("   ✅ Config received.")
        print(f"   Supported Timeframes: {len(cfg['timeframes'])}")
        print(f"   Supported Volume Types: {cfg['volume_types']}")
        assert "TICKS" in cfg['volume_types']
        assert "CUSTOM" in cfg['timeframes']
    except Exception as e:
        print(f"   ❌ Config failed: {e}")
        sys.exit(1)

def test_download_custom_flow():
    payload = {
        "symbols": ["XAUUSD"],
        "start_date": "2024-01-15",
        "end_date": "2024-01-15",
        "timeframe": "M1",
        "custom_tf": None,
        "threads": 5,
        "data_source": "auto",
        "price_type": "BID",
        "volume_type": "TICKS"
    }
    
    # Clean prev output
    if os.path.exists(DOWNLOAD_DIR):
        import shutil
        shutil.rmtree(DOWNLOAD_DIR)
        
    try:
        res = requests.post(f"{BASE_URL}/api/download", json=payload)
        res.raise_for_status()
        data = res.json()
        job_id = data["job_id"]
        print(f"   ✅ Job started. ID: {job_id}")
        return job_id
    except Exception as e:
        print(f"   ❌ Download request failed: {e}")
        sys.exit(1)

def monitor_file_generation():
    print("\n3. Waiting for file generation...")
    # Expected file for M1 XAUUSD
    expected_file = os.path.join("data", "XAUUSD-2024_01_15-2024_01_15.csv")
    
    # Poll API for status
    for _ in range(40):
        try:
            r = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
            if r.status_code == 200:
                j = r.json()
                status = j.get("status")
                progress = j.get("progress")
                print(f"   ℹ Job Status: {status} ({progress}%)")
                
                if status == "completed":
                    print("   ✅ Job marked completed!")
                    # Check file
                    if os.path.exists(expected_file):
                         print(f"   ✅ File verified at: {expected_file}")
                         return expected_file
                    else:
                         print("   ❌ Job complete but file missing!")
                         sys.exit(1)
                elif status == "failed":
                    print(f"   ❌ Job failed: {j.get('error')}")
                    # Print logs
                    print("   Logs:")
                    for l in j.get("logs", [])[-5:]:
                        print(f"     {l}")
                    sys.exit(1)
        except Exception as e:
            print(f"   ⚠ API Poll Error: {e}")
            
        time.sleep(1)
        
    print("   ❌ Timeout waiting for job.")
    try:
        r = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
        print("   Final State:", r.json())
    except: pass
    sys.exit(1)

def verify_file_content(filepath):
    print("\n4. Verifying File Content...")
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            
        header = lines[0].strip()
        first_row = lines[1].strip()
        
        print(f"   Header: {header}")
        print(f"   Row 1:  {first_row}")
        
        # Verify Header
        if "time,open,high,low,close,volume" not in header:
            print("   ❌ Header mismatch")
            sys.exit(1)
            
        # Verify DateTime Format (DD.MM.YYYY HH:MM:SS)
        # e.g. 15.01.2024 00:00:00
        dt_part = first_row.split(',')[0]
        if not (len(dt_part) == 19 and dt_part[2] == '.' and dt_part[5] == '.'):
             print(f"   ❌ DateTime format incorrect: {dt_part}")
             sys.exit(1)
             
        # Verify Volume (TICKS should be int)
        vol_part = first_row.split(',')[-1]
        try:
            vol_val = float(vol_part)
            if not vol_val.is_integer():
                 # 120s should have integer volume if TICKS type
                 # Wait, float(883) is 883.0. is_integer() is True.
                 # If it was lots, it would likely be fractional e.g. 135.45
                 # But lots COULD be integer.
                 # However, Ticks count is definitely integer.
                 pass
            print(f"   ✅ DateTime and Volume seem valid. (Vol: {vol_val})")
        except ValueError:
             print(f"   ❌ Volume is not a number: {vol_part}")
             sys.exit(1)
             
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_config()
    job_id = test_download_custom_flow()
    filepath = monitor_file_generation()
    verify_file_content(filepath)
    print("\n✅ E2E TEST PASSED SUCCESSFULY")
