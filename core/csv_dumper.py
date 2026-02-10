"""
CSV Dumper - Buffers tick data per day, aggregates to candles, and writes merged CSV.
Enhanced version of duka's csv_dumper.py with header support and volume in candles.
"""

import csv
import time
from os.path import join
from datetime import datetime

from core.candle import Candle
from config.settings import TimeFrame


# Output filename template: SYMBOL-STARTDATE_ENDDATE.csv
TEMPLATE_FILE_NAME = "{}-{}_{:02d}_{:02d}-{}_{:02d}_{:02d}.csv"


def format_float(number):
    """Format price to 5 decimal places."""
    return format(number, '.5f')


def stringify(timestamp):
    """Convert unix timestamp to datetime string."""
    return str(datetime.fromtimestamp(timestamp))


class CSVDumper:
    """
    Accumulates tick data per day, optionally aggregates to candles,
    and writes a single merged CSV file.
    """

    def __init__(self, symbol, timeframe, start, end, folder, header=True):
        self.symbol = symbol
        self.timeframe = timeframe
        self.start = start
        self.end = end
        self.folder = folder
        self.include_header = header
        self.buffer = {}  # {date: [ticks or candles]}

    def get_tick_header(self):
        return ['time', 'ask', 'bid', 'ask_volume', 'bid_volume']

    def get_candle_header(self):
        return ['time', 'open', 'high', 'low', 'close', 'volume']

    def get_header(self):
        if self.timeframe == TimeFrame.TICK:
            return self.get_tick_header()
        return self.get_candle_header()

    def append(self, day, ticks):
        """
        Buffer ticks for a given day.
        If timeframe != TICK, aggregate ticks into candles immediately.
        """
        self.buffer[day] = []

        if not ticks or len(ticks) == 0:
            return

        if self.timeframe == TimeFrame.TICK:
            self.buffer[day] = list(ticks)
            return

        # Aggregate ticks into candles (matching duka's bucketing logic)
        previous_key = None
        current_prices = []
        current_volumes = []

        for tick in ticks:
            ts = time.mktime(tick[0].timetuple())
            key = int(ts - (ts % self.timeframe))

            if previous_key != key and previous_key is not None:
                n = int((key - previous_key) / self.timeframe)
                for i in range(n):
                    candle = Candle(
                        self.symbol,
                        previous_key + i * self.timeframe,
                        self.timeframe,
                        current_prices if i == 0 else []
                    )
                    candle._volume = sum(current_volumes) if i == 0 else 0
                    self.buffer[day].append(candle)
                current_prices = []
                current_volumes = []

            current_prices.append(tick[1])  # Ask price
            current_volumes.append(tick[3] + tick[4])  # Total volume
            previous_key = key

        # Last candle
        if previous_key is not None and current_prices:
            candle = Candle(self.symbol, previous_key, self.timeframe, current_prices)
            candle._volume = sum(current_volumes)
            self.buffer[day].append(candle)

    def dump(self):
        """Write all buffered data to a single CSV file."""
        file_name = TEMPLATE_FILE_NAME.format(
            self.symbol,
            self.start.year, self.start.month, self.start.day,
            self.end.year, self.end.month, self.end.day,
        )

        file_path = join(self.folder, file_name)

        with open(file_path, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.get_header())

            if self.include_header:
                writer.writeheader()

            for day in sorted(self.buffer.keys()):
                for value in self.buffer[day]:
                    if self.timeframe == TimeFrame.TICK:
                        writer.writerow({
                            'time': value[0],
                            'ask': format_float(value[1]),
                            'bid': format_float(value[2]),
                            'ask_volume': value[3],
                            'bid_volume': value[4],
                        })
                    else:
                        writer.writerow({
                            'time': stringify(value.timestamp),
                            'open': format_float(value.open_price),
                            'high': format_float(value.high),
                            'low': format_float(value.low),
                            'close': format_float(value.close_price),
                            'volume': getattr(value, '_volume', 0),
                        })

        return file_path
