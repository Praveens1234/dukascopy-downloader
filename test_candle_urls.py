"""
Dukascopy Native Candle URL Discovery
Systematically tests ALL possible candle URL patterns against Dukascopy's servers
to discover which native timeframes are available.
"""

import requests
import struct
import lzma
import time

BASE = "https://datafeed.dukascopy.com/datafeed"
SYMBOL = "EURUSD"
YEAR = 2024
MONTH = 0   # 0-indexed (January)
DAY = 15

# ============================================================
# Test matrix: every combination of price type + timeframe
# ============================================================
PRICE_TYPES = ["BID", "ASK"]

# Possible timeframe naming patterns to test
# Format: (label, url_suffix, url_level)
# url_level: "day" = per-day file, "month" = per-month file, "year" = per-year file
TIMEFRAME_PATTERNS = [
    # === SECONDS ===
    ("SEC_10",   "candles_sec_10",   "day"),
    ("SEC_15",   "candles_sec_15",   "day"),
    ("SEC_30",   "candles_sec_30",   "day"),
    
    # === MINUTES ===
    ("M1",       "candles_min_1",    "day"),
    ("M2",       "candles_min_2",    "day"),
    ("M3",       "candles_min_3",    "day"),
    ("M5",       "candles_min_5",    "day"),
    ("M10",      "candles_min_10",   "day"),
    ("M15",      "candles_min_15",   "day"),
    ("M30",      "candles_min_30",   "day"),
    
    # === HOURS ===
    ("H1",       "candles_hour_1",   "month"),
    ("H2",       "candles_hour_2",   "month"),
    ("H4",       "candles_hour_4",   "month"),
    ("H8",       "candles_hour_8",   "month"),
    
    # === DAYS ===
    ("D1",       "candles_day_1",    "year"),
    
    # === WEEKS ===
    ("W1",       "candles_week_1",   "year"),
    
    # === MONTHS ===
    ("MN1",      "candles_month_1",  "year"),
    
    # === Alternative patterns (lowercase, different naming) ===
    ("tick_sec",  "candles_second_1", "day"),
    ("tick_sec10","candles_second_10","day"),
    ("M1_alt",    "candles_minute_1", "day"),
    ("H1_alt",    "candles_hourly_1", "month"),
    ("D1_alt",    "candles_daily_1",  "year"),
]


def build_url(price_type, suffix, level):
    """Build the full URL for a given pattern."""
    month_str = str(MONTH).zfill(2)
    day_str = str(DAY).zfill(2)
    
    if level == "day":
        return f"{BASE}/{SYMBOL}/{YEAR}/{month_str}/{day_str}/{price_type}_{suffix}.bi5"
    elif level == "month":
        return f"{BASE}/{SYMBOL}/{YEAR}/{month_str}/{price_type}_{suffix}.bi5"
    elif level == "year":
        return f"{BASE}/{SYMBOL}/{YEAR}/{price_type}_{suffix}.bi5"
    return None


def test_url(url, label):
    """Test if a URL returns valid candle data."""
    try:
        resp = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        })
        
        status = resp.status_code
        size = len(resp.content)
        
        if status == 200 and size > 0:
            # Try to decompress and parse
            try:
                data = lzma.decompress(resp.content)
                num_candles = len(data) // 24
                if num_candles > 0 and len(data) % 24 == 0:
                    # Parse first candle
                    ts, o, c, lo, hi, vol = struct.unpack_from(">IIIIIf", data, 0)
                    return {
                        "status": "✅ AVAILABLE",
                        "http": status,
                        "compressed": size,
                        "raw": len(data),
                        "candles": num_candles,
                        "sample": f"ts={ts} o={o/1e5:.5f} h={hi/1e5:.5f} l={lo/1e5:.5f} c={c/1e5:.5f} vol={vol:.1f}"
                    }
                else:
                    return {"status": "⚠️ DECOMPRESSED BUT INVALID FORMAT", "http": status, "raw": len(data)}
            except lzma.LZMAError:
                # Maybe not compressed?
                if size < 100:
                    return {"status": "❌ EMPTY/TINY", "http": status, "size": size}
                return {"status": "⚠️ NOT LZMA", "http": status, "size": size}
        elif status == 200 and size == 0:
            return {"status": "❌ EMPTY (200 but 0 bytes)", "http": status}
        else:
            return {"status": f"❌ HTTP {status}", "http": status}
    except requests.exceptions.Timeout:
        return {"status": "❌ TIMEOUT"}
    except Exception as e:
        return {"status": f"❌ ERROR: {str(e)[:50]}"}


def main():
    print("=" * 80)
    print("  DUKASCOPY NATIVE CANDLE URL DISCOVERY")
    print(f"  Symbol: {SYMBOL} | Year: {YEAR} | Month: {MONTH+1} | Day: {DAY}")
    print("=" * 80)
    
    results = []
    available = []
    
    for price_type in PRICE_TYPES:
        print(f"\n{'─' * 60}")
        print(f"  Testing {price_type} candles...")
        print(f"{'─' * 60}")
        
        for label, suffix, level in TIMEFRAME_PATTERNS:
            url = build_url(price_type, suffix, level)
            result = test_url(url, label)
            
            status_str = result["status"]
            extra = ""
            if "candles" in result:
                extra = f" | {result['candles']} candles | {result['sample']}"
                available.append((price_type, label, suffix, level, result["candles"]))
            
            print(f"  {price_type:3} {label:12} [{level:5}] → {status_str}{extra}")
            results.append((price_type, label, suffix, level, result))
            
            time.sleep(0.2)  # Rate limiting
    
    # Summary
    print(f"\n{'=' * 80}")
    print("  SUMMARY: AVAILABLE NATIVE CANDLES")
    print(f"{'=' * 80}")
    
    if available:
        print(f"\n  {'Price':5} {'TF':12} {'Level':6} {'URL Suffix':25} {'Candles':>8}")
        print(f"  {'─'*5} {'─'*12} {'─'*6} {'─'*25} {'─'*8}")
        for price, label, suffix, level, count in available:
            print(f"  {price:5} {label:12} {level:6} {suffix:25} {count:>8}")
    else:
        print("  No native candles found!")
    
    print(f"\n  Total patterns tested: {len(results)}")
    print(f"  Available: {len(available)}")
    print()


if __name__ == "__main__":
    main()
