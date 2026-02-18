from typing import Dict, Optional

class CandleMerger:
    """
    Merges chronologically sorted candle rows.
    Handles duplicate timestamps (e.g. crossing midnight) by merging OHLCV data.
    """
    def __init__(self):
        self.last_row: Optional[Dict[str, str]] = None

    def feed(self, row: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Feed a row.
        If the row's timestamp matches the buffered row, merge them.
        If the timestamp is different, yield the buffered row (it's complete) and buffer the new one.
        Returns:
            Dict representing a complete candle row, or None.
        """
        if self.last_row is None:
            self.last_row = row
            return None

        if row['time'] == self.last_row['time']:
            # Timestamp collision -> Merge parts of the same candle
            self.last_row = self._merge(self.last_row, row)
            return None
        else:
            # New timestamp -> Previous candle is complete
            result = self.last_row
            self.last_row = row
            return result

    def flush(self) -> Optional[Dict[str, str]]:
        """Return the last buffered row if any."""
        return self.last_row

    def _merge(self, r1: Dict[str, str], r2: Dict[str, str]) -> Dict[str, str]:
        """
        Merge two candle rows with same timestamp.
        Assumes r1 comes chronologically before r2 (from sorted part files).
        """
        # Parse values
        h1, l1, v1 = float(r1['high']), float(r1['low']), float(r1['volume'])
        h2, l2, v2 = float(r2['high']), float(r2['low']), float(r2['volume'])

        # Merge Logic:
        # Open: r1['open'] (first part's open)
        # Close: r2['close'] (last part's close)
        # High: max(h1, h2)
        # Low: min(l1, l2)
        # Volume: v1 + v2

        return {
            'time': r1['time'],
            'open': r1['open'],
            'high': format(max(h1, h2), '.5f'),
            'low': format(min(l1, l2), '.5f'),
            'close': r2['close'],
            'volume': str(round(v1 + v2, 2))  # Keep volume format consistent (2 decimals for float/sum)
            # Note: For volume type TICKS, it's integer, but float logic is safe enough if we format back.
            # Ideally volume handling depends on type, but sum is correct for all types except maybe ASK/BID splits?
            # Wait, volume types are aggregated in `append`. Summing them is correct.
        }
