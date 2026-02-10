"""
Progress tracker using tqdm.
Replaces duka's manual print('\r...') progress bar.
"""

from tqdm import tqdm


class DownloadProgress:
    """Track download progress with tqdm."""

    def __init__(self, total_days, symbol):
        self.total_days = total_days
        self.completed = 0
        self.failed = 0
        self.pbar = tqdm(
            total=total_days,
            desc=f"  {symbol}",
            unit="day",
            bar_format="{l_bar}{bar:30}{r_bar}",
            ncols=80,
        )

    def update(self, success=True):
        """Update progress by one day."""
        self.completed += 1
        if not success:
            self.failed += 1
        self.pbar.update(1)
        self.pbar.set_postfix({
            'ok': self.completed - self.failed,
            'fail': self.failed,
        })

    def close(self):
        self.pbar.close()


class MultiSymbolProgress:
    """Track progress for multiple symbols."""

    def __init__(self):
        self.trackers = {}

    def add_symbol(self, symbol, total_days):
        self.trackers[symbol] = DownloadProgress(total_days, symbol)

    def update(self, symbol, success=True):
        if symbol in self.trackers:
            self.trackers[symbol].update(success)

    def close_all(self):
        for tracker in self.trackers.values():
            tracker.close()
