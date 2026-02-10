"""
Logger utility - Console + file logging.
Production mode: suppress warnings from fetch retries to keep output clean.
"""

import logging
import sys


def get_logger(name='dukascopy', log_file=None, verbose=False):
    """
    Get a configured logger.
    Default: only show ERROR-level messages on console (clean output).
    Verbose mode: show WARNING and above.
    If log_file is specified, logs DEBUG and above to file.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler — ERROR only by default for clean progress bar output
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.ERROR if not verbose else logging.WARNING)
    console_fmt = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # File handler (all details go to file if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)

    return logger
