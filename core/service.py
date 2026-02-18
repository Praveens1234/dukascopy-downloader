import time
import threading
import concurrent.futures
from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Optional, Callable

from core.fetch import fetch_day
from core.processor import decompress
from core.csv_dumper import CSVDumper
from core.candle_fetch import fetch_native_candles
from core.validator import validate_output, print_validation_report
from core.exceptions import BackoffError
from config.settings import TimeFrame, NATIVE_CANDLE_TIMEFRAMES, SATURDAY, resolve_custom_timeframe
from utils.resume import save_state, load_state, clear_state
from utils.logger import get_logger
from utils.market import is_market_holiday

Logger = get_logger()

@dataclass
class DownloadConfig:
    symbols: List[str]
    start_date: date
    end_date: date
    timeframe: str
    threads: int
    data_source: str = 'auto'
    price_type: str = 'BID'
    volume_type: str = 'TOTAL'
    custom_tf: Optional[str] = None
    output_dir: str = '.'
    header: bool = True
    resume: bool = False

class ProgressObserver(ABC):
    @abstractmethod
    def on_start(self, symbol: str, total_days: int):
        pass

    @abstractmethod
    def on_update(self, symbol: str, days_processed: int, total_days: int, success: bool):
        pass

    @abstractmethod
    def on_finish(self, symbol: str, output_path: str):
        pass

    @abstractmethod
    def on_error(self, symbol: str, error: Exception):
        pass

    @abstractmethod
    def log(self, message: str):
        pass

class DownloaderService:
    def __init__(self, config: DownloadConfig, observer: ProgressObserver):
        self.config = config
        self._validate_symbols()
        self.observer = observer
        self._cancel_event = threading.Event()
        self._tf_value = self._resolve_timeframe()
        self._circuit_open = False
        self._circuit_reset_time = 0

    def _validate_symbols(self):
        import re
        for s in self.config.symbols:
            if not re.match(r'^[A-Z0-9]+$', s):
                raise ValueError(f"Invalid symbol format: {s}")

    def cancel(self):
        self._cancel_event.set()
        self.observer.log("Cancellation requested...")

    def _resolve_timeframe(self) -> int:
        if self.config.timeframe.upper() == 'CUSTOM' and self.config.custom_tf:
            return resolve_custom_timeframe(self.config.custom_tf)
        return getattr(TimeFrame, self.config.timeframe.upper(), TimeFrame.TICK)

    def _should_use_native(self) -> bool:
        tf_upper = self.config.timeframe.upper()
        if self.config.data_source == 'native':
            if tf_upper not in NATIVE_CANDLE_TIMEFRAMES:
                raise ValueError(f"Native candles not available for {tf_upper}")
            return True
        elif self.config.data_source == 'auto':
            return tf_upper in NATIVE_CANDLE_TIMEFRAMES and tf_upper != 'TICK'
        return False

    def _generate_days(self):
        current = self.config.start_date
        today = date.today()
        while current <= self.config.end_date:
            if current.weekday() != SATURDAY and current != today:
                yield current
            current += timedelta(days=1)

    def run(self):
        use_native = self._should_use_native()
        all_days = list(self._generate_days())
        total_days = len(all_days)

        if total_days == 0:
            self.observer.log("No trading days in the specified range.")
            return

        for symbol in self.config.symbols:
            if self._cancel_event.is_set():
                break

            try:
                if use_native:
                    self._process_native(symbol, total_days)
                else:
                    self._process_ticks(symbol, all_days)
            except Exception as e:
                self.observer.on_error(symbol, e)
                Logger.error(f"Error processing {symbol}: {e}")

    def _process_native(self, symbol: str, total_days: int):
        self.observer.on_start(symbol, total_days) # Native is treated as 1 step usually, but let's pass total
        self.observer.log(f"Fetching native {self.config.timeframe} candles...")

        csv_dumper = CSVDumper(
            symbol, self._tf_value, self.config.start_date, self.config.end_date,
            self.config.output_dir, self.config.header,
            self.config.price_type, self.config.volume_type
        )

        try:
            candles = fetch_native_candles(
                symbol, self.config.start_date, self.config.end_date,
                self.config.timeframe.upper(), self.config.price_type
            )
            csv_dumper.append_native_candles(candles)
            self.observer.log(f"Received {len(candles)} native candles.")

            file_path = csv_dumper.dump()
            self.observer.on_finish(symbol, file_path)

            # Update progress to 100% for this symbol
            self.observer.on_update(symbol, total_days, total_days, True)

        except Exception as e:
            raise e

    def _process_ticks(self, symbol: str, all_days: List[date]):
        # Resume Logic
        pending_days = all_days
        if self.config.resume:
            completed = load_state(self.config.output_dir, symbol)
            pending_days = [d for d in all_days if d not in completed]
            self.observer.log(f"Resuming: {len(all_days) - len(pending_days)} days already done.")

        # Holiday Filter
        non_holiday_days = []
        skipped_holidays = 0
        for d in pending_days:
            if is_market_holiday(d):
                skipped_holidays += 1
            else:
                non_holiday_days.append(d)

        if skipped_holidays > 0:
            self.observer.log(f"Skipping {skipped_holidays} market holidays.")

        pending_days = non_holiday_days

        if not pending_days:
            self.observer.log(f"All days already downloaded for {symbol}.")
            return

        self.observer.on_start(symbol, len(pending_days))

        csv_dumper = CSVDumper(
            symbol, self._tf_value, self.config.start_date, self.config.end_date,
            self.config.output_dir, self.config.header,
            self.config.price_type, self.config.volume_type
        )

        # Load previously completed days into memory for resume state tracking
        completed_list = []
        if self.config.resume:
            completed_list = load_state(self.config.output_dir, symbol)

        completed_count = 0
        lock = threading.Lock()

        def do_work(day):
            if self._cancel_event.is_set():
                return False

            # Circuit Breaker Check
            if self._circuit_open:
                if time.time() < self._circuit_reset_time:
                    return False
                else:
                    self._circuit_open = False # Reset

            try:
                raw_data = fetch_day(symbol, day)
                ticks = decompress(symbol, day, raw_data)

                with lock:
                    csv_dumper.append(day, ticks)
                    completed_list.append(day)

                return True
            except BackoffError as e:
                # Trigger Circuit Breaker
                with lock:
                    if not self._circuit_open:
                        self.observer.log(f"Backing off for 60s due to repeated 503s...")
                        self._circuit_open = True
                        self._circuit_reset_time = time.time() + 60
                return False
            except Exception as e:
                Logger.error(f"Error fetching {day}: {e}")
                return False

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.threads) as executor:
            futures = []
            for i, day in enumerate(pending_days):
                if self._cancel_event.is_set():
                    break

                futures.append(executor.submit(do_work, day))

                # Stagger requests
                if i > 0 and i % self.config.threads == 0:
                    time.sleep(0.5)

            for future in concurrent.futures.as_completed(futures):
                if self._cancel_event.is_set():
                    break

                success = future.result()
                with lock:
                    if success:
                         completed_count += 1
                    # Save state periodically
                    if (completed_count + 1) % 5 == 0:
                        save_state(self.config.output_dir, symbol, completed_list, all_days)

                self.observer.on_update(symbol, completed_count, len(pending_days), success)

        if self._cancel_event.is_set():
            self.observer.log("Download cancelled.")
            return

        file_path = csv_dumper.dump()
        self.observer.on_finish(symbol, file_path)
        clear_state(self.config.output_dir, symbol)
