"""
Candle (OHLC) class for aggregating tick data into candlesticks.
Ensures strict rounding to 5 decimal places for prices and 2 for volume.
"""

from datetime import datetime


class Candle:
    """Represents a single OHLC candlestick."""

    def __init__(self, symbol, timestamp, timeframe, sorted_values):
        """
        Args:
            symbol: Currency pair symbol
            timestamp: Unix timestamp (seconds) for candle start
            timeframe: Timeframe in seconds
            sorted_values: List of prices (ask prices) in chronological order
        """
        self.symbol = symbol
        self.timestamp = timestamp
        self.timeframe = timeframe

        if sorted_values:
            self.open_price = round(sorted_values[0], 5)
            self.close_price = round(sorted_values[-1], 5)
            self.high = round(max(sorted_values), 5)
            self.low = round(min(sorted_values), 5)
        else:
            self.open_price = 0.0
            self.close_price = 0.0
            self.high = 0.0
            self.low = 0.0

    def __str__(self):
        dt = datetime.utcfromtimestamp(self.timestamp)
        return (
            f"{dt} [{self.timestamp}] -- {self.symbol} -- "
            f"{{ H:{self.high} L:{self.low} O:{self.open_price} C:{self.close_price} }}"
        )

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (
            self.symbol == other.symbol
            and self.timestamp == other.timestamp
            and self.timeframe == other.timeframe
            and self.open_price == other.open_price
            and self.close_price == other.close_price
            and self.high == other.high
            and self.low == other.low
        )
