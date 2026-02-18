import struct
import lzma
import datetime
import pytest
from core.processor import decompress_lzma, tokenize, normalize_hour
from config.settings import DEFAULT_POINT_VALUE, VOLUME_MULTIPLIER

class TestProcessor:
    def test_decompress_lzma_valid(self):
        original = b"Hello World"
        compressed = lzma.compress(original)
        decompressed = decompress_lzma(compressed)
        assert decompressed == original

    def test_decompress_lzma_empty(self):
        assert decompress_lzma(b"") == b""

    def test_tokenize_valid(self):
        # Format: !IIIff (20 bytes)
        # time_ms, ask, bid, ask_vol, bid_vol
        # 100ms, 100000, 99990, 1.5, 1.2
        token = struct.pack('!IIIff', 100, 100000, 99990, 1.5, 1.2)
        tokens = tokenize(token)
        assert len(tokens) == 1

        t = tokens[0]
        assert t[0] == 100
        assert t[1] == 100000
        assert t[2] == 99990
        assert t[3] == pytest.approx(1.5, rel=1e-5)
        assert t[4] == pytest.approx(1.2, rel=1e-5)

    def test_normalize_hour(self):
        # We need to test the logic that converts raw data to human readable ticks
        symbol = "EURUSD" # Use default point value 100000
        day = datetime.date(2023, 1, 1)
        hour = 12

        # Manually create tokens list as if it came from tokenize()
        # (time_ms, ask_raw, bid_raw, ask_vol, bid_vol)
        tokens = [(100, 105000, 104990, 1.5, 1.2)]

        ticks = normalize_hour(symbol, day, hour, tokens)

        assert len(ticks) == 1
        dt, ask, bid, av, bv = ticks[0]

        # Expected datetime: 2023-01-01 12:00:00 + 100ms
        expected_dt = datetime.datetime(2023, 1, 1, 12, 0, 0, 100000)
        assert dt == expected_dt

        # Ask/Bid division by point value
        assert ask == pytest.approx(1.05000)
        assert bid == pytest.approx(1.04990)

        # Volume multiplier
        assert av == round(1.5 * VOLUME_MULTIPLIER)
        assert bv == round(1.2 * VOLUME_MULTIPLIER)
