import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner
from cli import main

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_fetch_day():
    with patch('core.service.fetch_day') as mock:
        # Return empty data to simulate no ticks -> no CSV rows but successful run
        # Or return valid compressed data?
        # Let's return valid compressed data to test decompression too?
        # Too complex. Let's return b"" (empty).
        # Wait, if empty, we get 0 ticks.
        # Let's return minimal valid data?
        # We need `lzma.compress(struct.pack(...))`

        import struct
        import lzma
        # 1 tick
        token = struct.pack('!IIIff', 100, 100000, 99990, 1.5, 1.2)
        data = lzma.compress(token)

        # fetch_day returns list of (hour, data)
        # return 1 hour of data
        mock.return_value = [(0, data)]
        yield mock

def test_cli_download_ticks(mock_fetch_day):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, [
            'EURUSD',
            '-s', '2023-01-01',
            '-e', '2023-01-02',
            '-t', 'TICK',
            '-o', '.'
        ])

        assert result.exit_code == 0
        assert "EURUSD-2023_01_01-2023_01_02.csv" in os.listdir('.')

def test_cli_download_candles(mock_fetch_day):
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, [
            'EURUSD',
            '-s', '2023-01-01',
            '-e', '2023-01-02',
            '-t', 'M1',
            '-o', '.'
        ])

        assert result.exit_code == 0
        # Verify file exists
        files = os.listdir('.')
        assert any(f.endswith('.csv') for f in files)
