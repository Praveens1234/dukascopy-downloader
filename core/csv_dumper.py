"""
CSV Dumper - Buffers tick data per day, aggregates to candles, and writes merged CSV.
Enhanced with UTC-safe bucketing, BID/ASK/MID price type support, volume type selection,
native candle mode, and DD.MM.YYYY HH:MM:SS datetime format.
"""

import csv
import calendar
from os.path import join
from datetime import datetime

from core.candle import Candle
from config.settings import TimeFrame


# Output filename template: SYMBOL-STARTDATE_ENDDATE.csv
TEMPLATE_FILE_NAME = "{}-{}_{:02d}_{:02d}-{}_{:02d}_{:02d}.csv"

# Datetime format for CSV output (DD.MM.YYYY HH:MM:SS, UTC)
DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'


def format_float(number):
    """Format price to 5 decimal places."""
    return format(number, '.5f')


def stringify_utc(unix_ts):
    """Convert unix timestamp to UTC datetime string in DD.MM.YYYY HH:MM:SS[.mmm] format."""
    dt = datetime.utcfromtimestamp(unix_ts)
    return format_datetime(dt)


def format_datetime(dt):
    """Format a datetime object to DD.MM.YYYY HH:MM:SS[.mmm]."""
    if isinstance(dt, datetime):
        s = dt.strftime(DATETIME_FORMAT)
        if dt.microsecond > 0:
            # Append milliseconds (first 3 digits of microsecond)
            ms = f"{dt.microsecond:06d}"[:3]
            return f"{s}.{ms}"
        return s
    return str(dt)


class CSVDumper:
    """
    Accumulates tick data per day, optionally aggregates to candles,
    and writes a single merged CSV file.

    Supports:
      - Tick output (raw ask/bid/volumes)
      - Tick-to-candle conversion with BID/ASK/MID price selection
      - Native candle data (pre-computed by Dukascopy)
    """

    def __init__(self, symbol, timeframe, start, end, folder, header=True,
                 price_type='BID', volume_type='TOTAL'):
        self.symbol = symbol
        self.timeframe = timeframe
        self.start = start
        self.end = end
        self.folder = folder
        self.include_header = header
        self.price_type = price_type.upper() if price_type else 'BID'
        self.volume_type = volume_type.upper() if volume_type else 'TOTAL'
        self.buffer = {}  # {date: [ticks or candles]}
        self.native_candles = []  # For native candle mode

    def get_tick_header(self):
        return ['time', 'ask', 'bid', 'ask_volume', 'bid_volume']

    def get_candle_header(self):
        return ['time', 'open', 'high', 'low', 'close', 'volume']

    def get_header(self):
        if self.timeframe == TimeFrame.TICK:
            return self.get_tick_header()
        return self.get_candle_header()

    def _get_price(self, tick):
        """Extract price from tick based on price_type setting.

        Tick format: (datetime, ask, bid, ask_volume, bid_volume)
        """
        if self.price_type == 'ASK':
            return tick[1]
        elif self.price_type == 'MID':
            return (tick[1] + tick[2]) / 2.0
        else:  # BID (default, matches Dukascopy website)
            return tick[2]

    def _get_volume(self, tick):
        """Extract volume from tick based on volume_type setting.

        Tick format: (datetime, ask, bid, ask_volume, bid_volume)
        """
        if self.volume_type == 'BID':
            return tick[4]
        elif self.volume_type == 'ASK':
            return tick[3]
        elif self.volume_type == 'TICKS':
            return 1  # Each tick counts as 1
        else:  # TOTAL (default)
            return tick[3] + tick[4]

    def append(self, day, ticks):
        """
        Buffer ticks for a given day.
        If timeframe != TICK, aggregate ticks into candles immediately.
        Uses UTC-safe bucketing (calendar.timegm instead of time.mktime).
        """
        self.buffer[day] = []

        if not ticks or len(ticks) == 0:
            return

        if self.timeframe == TimeFrame.TICK:
            self.buffer[day] = list(ticks)
            return

        # Aggregate ticks into candles using UTC timestamps
        previous_key = None
        current_prices = []
        current_volumes = []

        for tick in ticks:
            # Use calendar.timegm for UTC-safe timestamp (fixes timezone bucketing bug)
            ts = calendar.timegm(tick[0].timetuple())
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

            current_prices.append(self._get_price(tick))
            current_volumes.append(self._get_volume(tick))
            previous_key = key

        # Last candle
        if previous_key is not None and current_prices:
            candle = Candle(self.symbol, previous_key, self.timeframe, current_prices)
            candle._volume = sum(current_volumes)
            self.buffer[day].append(candle)

    def append_native_candles(self, candles):
        """
        Append pre-computed native candle data from Dukascopy.
        Each candle is (datetime, open, high, low, close, volume).
        """
        self.native_candles.extend(candles)

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

            # If we have native candles, write them directly
            if self.native_candles:
                self.native_candles.sort(key=lambda c: c[0])
                for c in self.native_candles:
                    writer.writerow({
                        'time': format_datetime(c[0]),
                        'open': format_float(c[1]),
                        'high': format_float(c[2]),
                        'low': format_float(c[3]),
                        'close': format_float(c[4]),
                        'volume': round(c[5], 2),
                    })
            else:
                # Write tick or tick-derived candle data
                for day in sorted(self.buffer.keys()):
                    for value in self.buffer[day]:
                        if self.timeframe == TimeFrame.TICK:
                            writer.writerow({
                                'time': format_datetime(value[0]),
                                'ask': format_float(value[1]),
                                'bid': format_float(value[2]),
                                'ask_volume': value[3],
                                'bid_volume': value[4],
                            })
                        else:
                            writer.writerow({
                                'time': stringify_utc(value.timestamp),
                                'open': format_float(value.open_price),
                                'high': format_float(value.high),
                                'low': format_float(value.low),
                                'close': format_float(value.close_price),
                                'volume': getattr(value, '_volume', 0),
                            })

        return file_path

