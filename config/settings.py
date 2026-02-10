"""
Dukascopy Downloader - Configuration Settings
Production-ready settings with anti-rate-limiting measures.
"""

# =============================================================================
# URL Template
# =============================================================================
URL_TEMPLATE = (
    "https://www.dukascopy.com/datafeed/"
    "{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
)

# =============================================================================
# HTTP Headers (browser-like to avoid 503 blocks)
# =============================================================================
HTTP_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://www.dukascopy.com/swiss/english/marketwatch/historical/",
}

# =============================================================================
# Download Settings
# =============================================================================
DEFAULT_THREADS = 5          # Conservative default to avoid 503s
MAX_THREADS = 30
DOWNLOAD_ATTEMPTS = 10       # More retries for production reliability
RETRY_BASE_DELAY = 1.0       # Base delay in seconds
RETRY_MAX_DELAY = 30.0       # Maximum delay between retries
HOURLY_CONCURRENCY = 8       # Max concurrent hourly downloads per day (not all 24 at once)
REQUEST_DELAY = 0.1          # Small delay (seconds) between starting each request
HTTP_TIMEOUT = 60             # Timeout per request in seconds

# =============================================================================
# Timeframes (in seconds)
# =============================================================================
class TimeFrame:
    TICK = 0
    M1   = 60
    M2   = 120
    M5   = 300
    M10  = 600
    M15  = 900
    M30  = 1800
    H1   = 3600
    H4   = 14400
    D1   = 86400

TIMEFRAME_CHOICES = ['TICK', 'M1', 'M2', 'M5', 'M10', 'M15', 'M30', 'H1', 'H4', 'D1']

# =============================================================================
# Price Point Values
# =============================================================================
SPECIAL_POINT_SYMBOLS = {
    'usdrub': 1000,
    'xagusd': 1000,
    'xauusd': 1000,
    'xaugbp': 1000,
    'xaueur': 1000,
    'xageur': 1000,
    'xaggbp': 1000,
}
DEFAULT_POINT_VALUE = 100000

# Volume multiplier
VOLUME_MULTIPLIER = 1_000_000

# =============================================================================
# Symbols
# =============================================================================
SYMBOLS = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'USDCHF',
    'AUDUSD', 'USDCAD', 'NZDUSD',
    'EURGBP', 'EURJPY', 'GBPJPY', 'EURAUD',
    'EURCAD', 'EURCHF', 'GBPCHF', 'GBPAUD',
    'AUDCAD', 'AUDCHF', 'AUDJPY', 'AUDNZD',
    'CADJPY', 'CADCHF', 'CHFJPY', 'NZDJPY',
    'NZDCAD', 'NZDCHF', 'GBPCAD', 'GBPNZD',
    'XAUUSD', 'XAGUSD',
    'USDRUB',
]

# =============================================================================
# Output Settings
# =============================================================================
DEFAULT_OUTPUT_DIR = '.'
DEFAULT_FORMAT = 'csv'

SATURDAY = 5
