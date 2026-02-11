"""
Dukascopy Downloader - Configuration Settings
Production-ready settings with anti-rate-limiting measures.
"""

# =============================================================================
# URL Templates
# =============================================================================
URL_TEMPLATE = (
    "https://www.dukascopy.com/datafeed/"
    "{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"
)

# Native candle URL templates (Dukascopy serves pre-computed OHLC for M1, H1, D1)
# Month is 0-indexed in Dukascopy URLs (00=Jan, 11=Dec)
CANDLE_URL_TEMPLATES = {
    'M1': "https://www.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{price_type}_candles_min_1.bi5",
    'H1': "https://www.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{price_type}_candles_hour_1.bi5",
    'D1': "https://www.dukascopy.com/datafeed/{currency}/{year}/{price_type}_candles_day_1.bi5",
}

# Timeframes that have native candle data on Dukascopy
NATIVE_CANDLE_TIMEFRAMES = {'M1', 'H1', 'D1'}

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
    S1   = 1
    S10  = 10
    S30  = 30
    M1   = 60
    M2   = 120
    M3   = 180
    M4   = 240
    M5   = 300
    M10  = 600
    M15  = 900
    M30  = 1800
    H1   = 3600
    H4   = 14400
    D1   = 86400

TIMEFRAME_CHOICES = [
    'TICK', 'S1', 'S10', 'S30',
    'M1', 'M2', 'M3', 'M4', 'M5', 'M10', 'M15', 'M30',
    'H1', 'H4', 'D1',
    'CUSTOM',
]


def resolve_custom_timeframe(value_str):
    """Resolve a custom timeframe string to seconds.

    Accepts:
        - Plain integer (seconds): '120' → 120
        - Suffixed: '30s' → 30, '5m' → 300, '2h' → 7200, '1d' → 86400
    Returns:
        int: timeframe in seconds
    Raises:
        ValueError: if format is invalid or value <= 0
    """
    value_str = value_str.strip().lower()
    multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}

    if value_str[-1] in multipliers:
        num = int(value_str[:-1])
        result = num * multipliers[value_str[-1]]
    else:
        result = int(value_str)

    if result <= 0:
        raise ValueError(f"Timeframe must be positive, got {result}")
    return result

# =============================================================================
# Data Source & Price Type
# =============================================================================
class DataSource:
    AUTO   = 'auto'    # Use native if available, else tick conversion
    TICK   = 'tick'    # Always fetch ticks and convert
    NATIVE = 'native'  # Use native candle data (only M1, H1, D1)

DATA_SOURCE_CHOICES = ['auto', 'tick', 'native']

class PriceType:
    BID = 'BID'
    ASK = 'ASK'
    MID = 'MID'

PRICE_TYPE_CHOICES = ['BID', 'ASK', 'MID']

class VolumeType:
    TOTAL = 'TOTAL'   # ask_volume + bid_volume (default)
    BID   = 'BID'     # bid_volume only
    ASK   = 'ASK'     # ask_volume only
    TICKS = 'TICKS'   # count of ticks in candle

VOLUME_TYPE_CHOICES = ['TOTAL', 'BID', 'ASK', 'TICKS']

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
