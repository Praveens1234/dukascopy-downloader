import pytest
from core.candle import Candle
from core.aggregator import CandleMerger

class TestCandle:
    def test_candle_init(self):
        # timestamps don't matter much for logic, just identity
        c = Candle("TEST", 1000, 60, [1.0, 2.0, 0.5, 1.5])
        assert c.open_price == 1.0
        assert c.close_price == 1.5
        assert c.high == 2.0
        assert c.low == 0.5

    def test_candle_empty(self):
        c = Candle("TEST", 1000, 60, [])
        assert c.open_price == 0.0
        assert c.high == 0.0

    def test_candle_rounding(self):
        # 1.000001 -> 1.00000
        c = Candle("TEST", 1000, 60, [1.000001, 1.000009])
        assert c.open_price == 1.00000
        assert c.close_price == 1.00001

class TestMerger:
    def test_merger_logic(self):
        merger = CandleMerger()

        row1 = {
            'time': '01.01.2023 00:00:00',
            'open': '1.0',
            'high': '1.5',
            'low': '0.9',
            'close': '1.2', # Intermediate close
            'volume': '100.0'
        }

        row2 = {
            'time': '01.01.2023 00:00:00', # SAME TIME
            'open': '1.2', # Intermediate open (should be ignored, we take row1 open)
            'high': '1.6', # Higher high
            'low': '1.0', # Higher low (so 0.9 remains min)
            'close': '1.4', # Final close
            'volume': '50.0'
        }

        assert merger.feed(row1) is None # Buffer
        assert merger.feed(row2) is None # Merge

        # New row flush
        row3 = {
            'time': '01.01.2023 01:00:00',
            'open': '2.0',
            'high': '2.0',
            'low': '2.0',
            'close': '2.0',
            'volume': '10.0'
        }

        result = merger.feed(row3)
        assert result is not None
        assert result['time'] == '01.01.2023 00:00:00'
        assert result['open'] == '1.0'
        assert result['close'] == '1.4'
        assert result['high'] == '1.60000' # formatted string
        assert result['low'] == '0.90000'
        assert result['volume'] == '150.0'

        last = merger.flush()
        assert last == row3
