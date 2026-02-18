"""
Logger utility - Console + file logging.
Production mode: suppress warnings from fetch retries to keep output clean.
Logs everything to 'download.log' with rotation.
"""

import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def get_logger(name='dukascopy', log_file='download.log', verbose=False):
    """
    Get a configured logger.
    Default: only show INFO/ERROR-level messages on console (clean output).
    Always logs DEBUG and above to 'download.log'.
    """
    logger = logging.getLogger(name)
    logger.propagate = False # Prevent double logging if root logger is configured

    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Console handler — INFO/ERROR only by default for clean progress bar output
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.INFO if verbose else logging.WARNING)
    console_fmt = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_fmt)
    logger.addHandler(console_handler)

    # File handler (all details go to file)
    try:
        # 5 MB per file, max 3 backups
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(threadName)s - %(message)s'
        )
        file_handler.setFormatter(file_fmt)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not set up file logging: {e}", file=sys.stderr)

    return logger
