"""
Unit tests for the forward-fill filter that removes fake Dukascopy candles/ticks
injected during market closures (weekends, holidays, daily server resets).
"""

import sys
import os
import struct
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.processor import _filter_forward_filled_ticks
from core.candle_fetch import parse_candles, CANDLE_STRUCT, CANDLE_SIZE


class TestTickForwardFillFilter:
    """Tests for _filter_forward_filled_ticks in processor.py."""

    def test_empty_input(self):
        result = _filter_forward_filled_ticks([])
        assert result == []

    def test_single_tick_preserved(self):
        ticks = [(datetime(2026, 1, 2, 0, 0), 100.0, 99.5, 500, 600)]
        result = _filter_forward_filled_ticks(ticks)
        assert len(result) == 1

    def test_unique_ticks_preserved(self):
        """All different ticks should pass through."""
        ticks = [
            (datetime(2026, 1, 2, 0, 0), 100.0, 99.5, 500, 600),
            (datetime(2026, 1, 2, 0, 1), 100.5, 100.0, 510, 610),
            (datetime(2026, 1, 2, 0, 2), 101.0, 100.5, 520, 620),
        ]
        result = _filter_forward_filled_ticks(ticks)
        assert len(result) == 3

    def test_consecutive_duplicates_removed(self):
        """Forward-filled duplicate ticks should be removed."""
        ticks = [
            (datetime(2026, 1, 2, 21, 59), 100.0, 99.5, 500, 600),  # Real
            (datetime(2026, 1, 2, 22, 0), 100.0, 99.5, 500, 600),   # Fake (dup)
            (datetime(2026, 1, 2, 22, 1), 100.0, 99.5, 500, 600),   # Fake (dup)
            (datetime(2026, 1, 2, 22, 2), 100.0, 99.5, 500, 600),   # Fake (dup)
            (datetime(2026, 1, 2, 23, 0), 101.0, 100.5, 520, 620),  # Real (new values)
        ]
        result = _filter_forward_filled_ticks(ticks)
        assert len(result) == 2
        assert result[0][0] == datetime(2026, 1, 2, 21, 59)
        assert result[1][0] == datetime(2026, 1, 2, 23, 0)

    def test_non_consecutive_duplicates_preserved(self):
        """Same values appearing after different values should be kept."""
        ticks = [
            (datetime(2026, 1, 2, 0, 0), 100.0, 99.5, 500, 600),
            (datetime(2026, 1, 2, 0, 1), 101.0, 100.5, 510, 610),  # Different
            (datetime(2026, 1, 2, 0, 2), 100.0, 99.5, 500, 600),   # Same as [0] but not consecutive — keep
        ]
        result = _filter_forward_filled_ticks(ticks)
        assert len(result) == 3

    def test_weekend_scenario(self):
        """Simulate a full weekend of duplicated ticks (all should be removed except first)."""
        base_tick = (100.0, 99.5, 500, 600)
        ticks = []
        # 2880 minutes of forward-fill (48 hours weekend)
        for i in range(2880):
            dt = datetime(2026, 1, 3, 0, 0) + timedelta(minutes=i)
            ticks.append((dt, *base_tick))

        result = _filter_forward_filled_ticks(ticks)
        assert len(result) == 1  # Only the first tick should remain


class TestNativeCandleForwardFillFilter:
    """Tests for parse_candles forward-fill filter in candle_fetch.py."""

    def _make_raw_candle(self, time_offset, raw_open, raw_close, raw_low, raw_high, volume):
        """Create raw binary data for a single candle."""
        return CANDLE_STRUCT.pack(time_offset, raw_open, raw_close, raw_low, raw_high, volume)

    def test_unique_candles_preserved(self):
        """All different candles should pass through."""
        raw = b''
        raw += self._make_raw_candle(0, 1000, 1010, 990, 1020, 100.0)
        raw += self._make_raw_candle(60, 1010, 1020, 1000, 1030, 110.0)
        raw += self._make_raw_candle(120, 1020, 1030, 1010, 1040, 120.0)

        base_time = datetime(2026, 1, 2, 0, 0, 0)
        candles = parse_candles(raw, base_time, 'EURUSD')
        assert len(candles) == 3

    def test_forward_filled_candles_removed(self):
        """Consecutive duplicate OHLCV candles should be filtered."""
        raw = b''
        raw += self._make_raw_candle(0, 1000, 1010, 990, 1020, 100.0)       # Real
        raw += self._make_raw_candle(60, 1000, 1010, 990, 1020, 100.0)      # Fake (dup)
        raw += self._make_raw_candle(120, 1000, 1010, 990, 1020, 100.0)     # Fake (dup)
        raw += self._make_raw_candle(180, 1020, 1030, 1010, 1040, 120.0)    # Real (new values)

        base_time = datetime(2026, 1, 2, 0, 0, 0)
        candles = parse_candles(raw, base_time, 'EURUSD')
        assert len(candles) == 2
        assert candles[0][0] == datetime(2026, 1, 2, 0, 0, 0)
        assert candles[1][0] == datetime(2026, 1, 2, 0, 3, 0)

    def test_all_zero_candles_removed(self):
        """All-zero candles should be filtered."""
        raw = b''
        raw += self._make_raw_candle(0, 1000, 1010, 990, 1020, 100.0)
        raw += self._make_raw_candle(60, 0, 0, 0, 0, 0.0)
        raw += self._make_raw_candle(120, 1020, 1030, 1010, 1040, 120.0)

        base_time = datetime(2026, 1, 2, 0, 0, 0)
        candles = parse_candles(raw, base_time, 'EURUSD')
        assert len(candles) == 2

    def test_full_day_weekend_simulation(self):
        """Simulate a Saturday: 1440 candles all with same OHLCV. Should return just 1."""
        raw = b''
        for i in range(1440):
            raw += self._make_raw_candle(i * 60, 4331575, 4331575, 4331575, 4331575, 0.0)

        base_time = datetime(2026, 1, 3, 0, 0, 0)  # Saturday
        candles = parse_candles(raw, base_time, 'XAUUSD')
        assert len(candles) == 1  # Only the first unique candle

    def test_holiday_partial_data(self):
        """Simulate holiday: 1380 forward-filled + 60 real candles."""
        raw = b''
        # First 1380: all forward-filled (same OHLCV)
        for i in range(1380):
            raw += self._make_raw_candle(i * 60, 4318679, 4318679, 4318679, 4318679, 0.0)
        # Last 60: real trading data (different OHLCV each)
        for i in range(60):
            offset = (1380 + i) * 60
            price = 4323698 + i * 100
            raw += self._make_raw_candle(offset, price, price + 50, price - 30, price + 80, 0.0)

        base_time = datetime(2026, 1, 1, 0, 0, 0)
        candles = parse_candles(raw, base_time, 'XAUUSD')
        assert len(candles) == 61  # 1 unique forward-fill + 60 real candles

    def test_xauusd_point_value(self):
        """Verify XAUUSD uses point value of 1000."""
        raw = self._make_raw_candle(0, 4331575, 4331575, 4331575, 4331575, 0.0)
        base_time = datetime(2026, 1, 3, 0, 0, 0)
        candles = parse_candles(raw, base_time, 'XAUUSD')
        assert len(candles) == 1
        # 4331575 / 1000 = 4331.575
        assert abs(candles[0][1] - 4331.575) < 0.001


def run_tests():
    """Simple test runner."""
    test_classes = [TestTickForwardFillFilter, TestNativeCandleForwardFillFilter]
    total = 0
    passed = 0
    failed = 0

    for cls in test_classes:
        print(f"\n{'='*60}")
        print(f"  {cls.__name__}")
        print(f"{'='*60}")

        instance = cls()
        methods = [m for m in dir(instance) if m.startswith('test_')]

        for method_name in sorted(methods):
            total += 1
            try:
                getattr(instance, method_name)()
                print(f"  ✓ {method_name}")
                passed += 1
            except AssertionError as e:
                print(f"  ✗ {method_name}: {e}")
                failed += 1
            except Exception as e:
                print(f"  ✗ {method_name}: EXCEPTION — {e}")
                failed += 1

    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    print(f"{'='*60}")
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
