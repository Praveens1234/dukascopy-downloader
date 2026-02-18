"""
CSV Dumper - Streaming implementation.
Buffers data to temporary files per day to keep memory usage low,
then merges them into a sorted final CSV.
"""

import csv
import calendar
import shutil
import os
import glob
from os.path import join
from datetime import datetime, date

from core.candle import Candle
from core.aggregator import CandleMerger
from config.settings import TimeFrame

# Output filename template: SYMBOL-STARTDATE_ENDDATE.csv
TEMPLATE_FILE_NAME = "{}-{}_{:02d}_{:02d}-{}_{:02d}_{:02d}.csv"

# Datetime format for CSV output (DD.MM.YYYY HH:MM:SS, UTC)
DATETIME_FORMAT = '%d.%m.%Y %H:%M:%S'

def format_float(number):
    """Format price to 5 decimal places."""
    return format(number, '.5f')

def stringify_utc(unix_ts):
    """Convert unix timestamp to UTC datetime string in DD.MM.YYYY HH:MM:SS format."""
    return datetime.utcfromtimestamp(unix_ts).strftime(DATETIME_FORMAT)

def format_datetime(dt):
    """Format a datetime object to DD.MM.YYYY HH:MM:SS."""
    if isinstance(dt, datetime):
        return dt.strftime(DATETIME_FORMAT)
    return str(dt)

class CSVDumper:
    """
    Streaming CSV Dumper.
    Writes chunks to temporary files to avoid OOM on large datasets.
    Merges sorted chunks at the end.
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

        # Create a temp directory for this specific download
        self.temp_dir = join(folder, f".temp_{symbol}_{int(datetime.now().timestamp())}")
        os.makedirs(self.temp_dir, exist_ok=True)

        self.native_buffer = []

    def get_tick_header(self):
        return ['time', 'ask', 'bid', 'ask_volume', 'bid_volume']

    def get_candle_header(self):
        return ['time', 'open', 'high', 'low', 'close', 'volume']

    def get_header(self):
        if self.timeframe == TimeFrame.TICK:
            return self.get_tick_header()
        return self.get_candle_header()

    def _get_price(self, tick):
        if self.price_type == 'ASK':
            return tick[1]
        elif self.price_type == 'MID':
            return (tick[1] + tick[2]) / 2.0
        else:  # BID
            return tick[2]

    def _get_volume(self, tick):
        if self.volume_type == 'BID':
            return tick[4]
        elif self.volume_type == 'ASK':
            return tick[3]
        elif self.volume_type == 'TICKS':
            return 1
        else:  # TOTAL
            return tick[3] + tick[4]

    def _write_chunk(self, filename, rows):
        """Write a list of dicts to a temp CSV file."""
        if not rows:
            return
        path = join(self.temp_dir, filename)
        # We don't write headers in chunks, only data
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.get_header())
            writer.writerows(rows)

    def append(self, day, ticks):
        """
        Process ticks for a day and write to a temp file.
        """
        if not ticks:
            return

        rows = []

        if self.timeframe == TimeFrame.TICK:
            for tick in ticks:
                rows.append({
                    'time': format_datetime(tick[0]),
                    'ask': format_float(tick[1]),
                    'bid': format_float(tick[2]),
                    'ask_volume': tick[3],
                    'bid_volume': tick[4],
                })
        else:
            # Aggregate to candles (per day)
            previous_key = None
            current_prices = []
            current_volumes = []

            for tick in ticks:
                ts = calendar.timegm(tick[0].timetuple())
                key = int(ts - (ts % self.timeframe))

                if previous_key != key and previous_key is not None:
                    n = int((key - previous_key) / self.timeframe)
                    for i in range(n):
                        candle_prices = current_prices if i == 0 else []
                        candle_vol = sum(current_volumes) if i == 0 else 0

                        candle = Candle(self.symbol, previous_key + i * self.timeframe, self.timeframe, candle_prices)
                        rows.append({
                            'time': stringify_utc(candle.timestamp),
                            'open': format_float(candle.open_price),
                            'high': format_float(candle.high),
                            'low': format_float(candle.low),
                            'close': format_float(candle.close_price),
                            'volume': candle_vol,
                        })

                    current_prices = []
                    current_volumes = []

                current_prices.append(self._get_price(tick))
                current_volumes.append(self._get_volume(tick))
                previous_key = key

            if previous_key is not None and current_prices:
                candle = Candle(self.symbol, previous_key, self.timeframe, current_prices)
                candle_vol = sum(current_volumes)
                rows.append({
                    'time': stringify_utc(candle.timestamp),
                    'open': format_float(candle.open_price),
                    'high': format_float(candle.high),
                    'low': format_float(candle.low),
                    'close': format_float(candle.close_price),
                    'volume': candle_vol,
                })

        if rows:
            self._write_chunk(f"{day.toordinal()}.part", rows)


    def append_native_candles(self, candles):
        """Append native candles."""
        if not candles:
            return

        rows = []
        for c in candles:
             rows.append({
                'time': format_datetime(c[0]),
                'open': format_float(c[1]),
                'high': format_float(c[2]),
                'low': format_float(c[3]),
                'close': format_float(c[4]),
                'volume': round(c[5], 2),
            })
        self._write_chunk("native.part", rows)


    def dump(self):
        """Merge all temp files into the final CSV."""
        file_name = TEMPLATE_FILE_NAME.format(
            self.symbol,
            self.start.year, self.start.month, self.start.day,
            self.end.year, self.end.month, self.end.day,
        )

        file_path = join(self.folder, file_name)

        parts = sorted(glob.glob(join(self.temp_dir, "*.part")))
        is_candle = (self.timeframe != TimeFrame.TICK)

        merger = CandleMerger() if is_candle else None

        with open(file_path, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=self.get_header())
            if self.include_header:
                writer.writeheader()

            for part in parts:
                with open(part, 'r') as infile:
                    if not is_candle:
                        # Fast path for ticks
                        shutil.copyfileobj(infile, outfile)
                    else:
                        # Merge path for candles
                        # Since part files have NO header, we pass fieldnames
                        reader = csv.DictReader(infile, fieldnames=self.get_header())
                        for row in reader:
                            to_write = merger.feed(row)
                            if to_write:
                                writer.writerow(to_write)

            # Flush last candle if any
            if is_candle:
                last = merger.flush()
                if last:
                    writer.writerow(last)

        # Cleanup
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass

        return file_path
