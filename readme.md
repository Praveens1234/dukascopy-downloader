# Dukascopy Historical Data Downloader

<p align="center">
  <strong>A production-ready tool for downloading high-quality historical forex and CFD tick/candle data from Dukascopy Bank SA</strong>
</p>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-api-reference">API Reference</a> •
  <a href="#-configuration">Configuration</a>
</p>

---

## Overview

Dukascopy Historical Data Downloader is a robust, production-grade Python application that enables users to download historical tick and OHLC candle data from Dukascopy Bank's datafeed. The tool provides both a modern **Web UI** for interactive use and a powerful **Command Line Interface (CLI)** for automation and batch processing.

### Why This Tool?

Dukascopy Bank provides free access to high-quality historical forex data, but downloading it reliably presents several challenges:

- **Rate Limiting**: Dukascopy enforces strict rate limits that can result in HTTP 503 errors
- **Data Complexity**: Tick data is stored in compressed binary format (.bi5) requiring specialized parsing
- **Time Precision**: Proper timestamp handling across different timeframes and timezones
- **Resume Capability**: Large downloads often need to be interrupted and resumed

This tool addresses all these challenges with production-ready solutions including exponential backoff, browser-like request emulation, resumable downloads, and comprehensive data validation.

---

## Features

### Data Acquisition

| Feature | Description |
|---------|-------------|
| **Tick Data** | Download raw tick-by-tick data with millisecond precision (ask/bid prices and volumes) |
| **Native Candles** | Fetch pre-computed OHLC candles directly from Dukascopy (M1, H1, D1) |
| **Tick-to-Candle** | Convert tick data to any custom timeframe (S1 through D1) |
| **Multiple Symbols** | Download data for 30+ forex pairs, precious metals (XAUUSD, XAGUSD), and more |
| **Price Types** | Choose between BID, ASK, or MID (average) price calculations |
| **Volume Types** | Select TOTAL, BID-only, ASK-only volumes, or tick counts |

### Robustness & Reliability

- **Anti-Rate-Limiting**: Browser-like headers, exponential backoff with random jitter, and request staggering to avoid HTTP 503 blocks
- **Resumable Downloads**: State is saved every 5 days; interrupted downloads can be resumed with `--resume`
- **Data Validation**: Post-download validation ensures chronological ordering and price sanity checks
- **Error Handling**: Graceful degradation with detailed logging; corrupted files are skipped without crashing

### User Interfaces

#### Web UI
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Live Monitoring**: Real-time progress bars and streaming terminal logs via WebSocket
- **Job Management**: Start, monitor, and cancel downloads from the browser
- **File Manager**: Browse, download, and delete exported CSV files directly from the UI
- **Custom Symbols**: Add any symbol (e.g., BTCUSD, ETHUSD) beyond the predefined list

#### CLI
- **Batch Processing**: Download multiple symbols and date ranges in one command
- **Automation-Friendly**: Perfect for cron jobs, scripts, and CI/CD pipelines
- **Flexible Output**: Tick data or aggregated candles in multiple timeframes

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Quick Install

```bash
# Clone the repository
git clone https://github.com/Praveens1234/dukascopy-downloader.git
cd dukascopy-downloader

# Install dependencies
pip install -r requirements.txt
```

### Dependencies

| Package | Purpose |
|---------|---------|
| `aiohttp >= 3.8.0` | Async HTTP client for downloading data |
| `tqdm >= 4.64.0` | Progress bars for CLI |
| `click >= 8.0.0` | CLI argument parsing |
| `fastapi >= 0.104.0` | Web server framework |
| `uvicorn[standard] >= 0.24.0` | ASGI server |
| `python-multipart >= 0.0.6` | Form data parsing |

---

## Quick Start

### Option 1: Web UI (Recommended)

Start the web server and access the downloader from your browser:

```bash
python server.py
```

The server will:
- Start on `http://localhost:8000`
- Automatically open your browser
- Display a network URL for mobile access (e.g., `http://192.168.1.5:8000`)

### Option 2: Command Line

Download EURUSD minute data for January 2024:

```bash
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t M1
```

---

## Usage

### Web UI Guide

#### 1. Starting a Download

Navigate to the **New Download** tab and configure:

1. **Symbols**: Click on symbol chips to select/deselect, or type custom symbols in the input field
2. **Date Range**: Select start and end dates (YYYY-MM-DD format)
3. **Timeframe**: Choose from TICK, S1, S10, S30, M1, M2, M3, M4, M5, M10, M15, M30, H1, H4, D1, or Custom
4. **Data Source**:
   - `Auto` (Recommended): Uses native candles if available, falls back to tick conversion
   - `Tick → Candle`: Always fetches ticks and converts to candles
   - `Native OHLC`: Uses only pre-computed candles from Dukascopy (M1, H1, D1 only)
5. **Price Type**: BID (default), ASK, or MID (average)
6. **Volume Type**: TOTAL (ask+bid), BID-only, ASK-only, or TICKS (count)
7. **Threads**: Slider from 1-20 (default: 5 is recommended for stability)

#### 2. Monitoring Downloads

- **Progress Panel**: Shows real-time progress percentage and days completed
- **Terminal Tab**: Live streaming logs with timestamps
- **Jobs Tab**: View all download history and their statuses

#### 3. Managing Files

The **Files** tab allows you to:
- View all exported CSV files with size and modification time
- Download files to your local machine
- Delete files you no longer need

### CLI Reference

#### Basic Syntax

```bash
python cli.py SYMBOLS -s START_DATE -e END_DATE [OPTIONS]
```

#### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `SYMBOLS` | One or more currency pairs | `EURUSD GBPUSD XAUUSD` |
| `-s, --start` | Start date (YYYY-MM-DD) | `-s 2024-01-01` |
| `-e, --end` | End date (YYYY-MM-DD) | `-e 2024-12-31` |

#### Optional Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `-t, --timeframe` | `TICK` | Data timeframe (see table below) |
| `--custom-tf` | - | Custom timeframe (e.g., `120`, `5m`, `2h`) |
| `--threads` | `5` | Number of parallel download threads |
| `-o, --output` | `.` | Output directory |
| `--header/--no-header` | `True` | Include CSV header row |
| `--resume` | `False` | Resume interrupted download |
| `--source` | `auto` | Data source: `auto`, `tick`, or `native` |
| `--price-type` | `BID` | Price type: `BID`, `ASK`, or `MID` |
| `--volume-type` | `TOTAL` | Volume type: `TOTAL`, `BID`, `ASK`, `TICKS` |

#### Supported Timeframes

| Type | Values | Description |
|------|--------|-------------|
| **Tick** | `TICK` | Raw tick data (highest precision) |
| **Seconds** | `S1`, `S10`, `S30` | 1-second, 10-second, 30-second candles |
| **Minutes** | `M1`, `M2`, `M3`, `M4`, `M5`, `M10`, `M15`, `M30` | Various minute candles |
| **Hours** | `H1`, `H4` | 1-hour and 4-hour candles |
| **Days** | `D1` | Daily candles |
| **Custom** | `CUSTOM` | Use with `--custom-tf` for arbitrary intervals |

#### CLI Examples

```bash
# Download raw tick data
python cli.py EURUSD -s 2024-01-01 -e 2024-01-02 -t TICK

# Download multiple symbols as M1 candles
python cli.py EURUSD GBPUSD XAUUSD -s 2024-01-01 -e 2024-12-31 -t M1

# Download with native candle source (faster)
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1 --source native

# Resume an interrupted download
python cli.py EURUSD -s 2020-01-01 -e 2024-12-31 --resume

# Custom timeframe (2-hour candles)
python cli.py EURUSD -s 2024-01-01 -e 2024-06-01 -t CUSTOM --custom-tf 2h

# Custom timeframe in seconds (90-second candles)
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 90

# Download with specific price and volume types
python cli.py XAUUSD -s 2024-01-01 -e 2024-12-31 -t H1 --price-type ASK --volume-type TICKS

# Increase threads for faster download (use cautiously)
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1 --threads 10
```

---

## API Reference

The Web UI is powered by a FastAPI backend with the following REST endpoints:

### GET `/api/config`

Returns available symbols, timeframes, and configuration defaults.

**Response:**
```json
{
  "symbols": ["EURUSD", "GBPUSD", ...],
  "timeframes": ["TICK", "S1", "M1", ...],
  "default_threads": 5,
  "max_threads": 30,
  "volume_types": ["TOTAL", "BID", "ASK", "TICKS"]
}
```

### POST `/api/download`

Start a new download job.

**Request Body:**
```json
{
  "symbols": ["EURUSD", "GBPUSD"],
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "timeframe": "M1",
  "threads": 5,
  "data_source": "auto",
  "price_type": "BID",
  "volume_type": "TOTAL",
  "custom_tf": null
}
```

**Response:**
```json
{
  "job_id": "a1b2c3d4",
  "status": "started"
}
```

### GET `/api/jobs/{job_id}`

Get the status and details of a specific job.

**Response:**
```json
{
  "id": "a1b2c3d4",
  "status": "running",
  "progress": 45.5,
  "total_days": 365,
  "completed_days": 166,
  "logs": ["[10:30:15] Starting download..."],
  "started_at": "2024-01-15T10:30:00",
  "finished_at": null,
  "output_file": null,
  "error": null
}
```

### POST `/api/jobs/{job_id}/cancel`

Cancel a running job.

### GET `/api/jobs`

List all jobs (most recent first).

### GET `/api/files`

List all CSV files in the data directory.

### GET `/api/files/{filename}`

Download a specific CSV file.

### DELETE `/api/files/{filename}`

Delete a specific CSV file.

### WebSocket `/ws`

Connect for real-time log streaming and progress updates.

**Message Types:**
- `{"type": "log", "job_id": "...", "message": "..."}`
- `{"type": "progress", "job_id": "...", "status": "...", "progress": 45.5}`

---

## Output Format

### File Naming

Files are saved with the pattern: `{SYMBOL}-{START_DATE}-{END_DATE}.csv`

**Example:** `EURUSD-2024_01_01-2024_12_31.csv`

### CSV Format

#### Tick Data
```csv
time,ask,bid,ask_volume,bid_volume
01.01.2024 00:00:00.123,1.10425,1.10420,150,200
01.01.2024 00:00:00.456,1.10430,1.10425,100,150
```

#### Candle Data (OHLCV)
```csv
time,open,high,low,close,volume
01.01.2024 00:00:00,1.10420,1.10435,1.10415,1.10430,1250.5
01.01.2024 00:01:00,1.10430,1.10445,1.10425,1.10440,980.25
```

### Datetime Format

All timestamps are in **UTC** and formatted as: `DD.MM.YYYY HH:MM:SS[.mmm]`

- Tick data includes milliseconds (`.mmm`)
- Candle data uses whole seconds

---

## Configuration

All configurable settings are in `config/settings.py`:

### Download Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `DEFAULT_THREADS` | 5 | Default number of download threads |
| `MAX_THREADS` | 30 | Maximum allowed threads |
| `DOWNLOAD_ATTEMPTS` | 10 | Retries per file before giving up |
| `RETRY_BASE_DELAY` | 1.0s | Base delay for exponential backoff |
| `RETRY_MAX_DELAY` | 30.0s | Maximum delay between retries |
| `HOURLY_CONCURRENCY` | 8 | Max concurrent hourly file downloads |
| `REQUEST_DELAY` | 0.1s | Delay between starting each request |
| `HTTP_TIMEOUT` | 60s | Timeout per HTTP request |

### URL Templates

The tool uses Dukascopy's datafeed URLs:

- **Tick Data**: `https://www.dukascopy.com/datafeed/{symbol}/{year}/{month}/{day}/{hour}h_ticks.bi5`
- **M1 Candles**: `https://www.dukascopy.com/datafeed/{symbol}/{year}/{month}/{day}/{price_type}_candles_min_1.bi5`
- **H1 Candles**: `https://www.dukascopy.com/datafeed/{symbol}/{year}/{month}/{price_type}_candles_hour_1.bi5`
- **D1 Candles**: `https://www.dukascopy.com/datafeed/{symbol}/{year}/{price_type}_candles_day_1.bi5`

### Supported Symbols

```
Major Pairs: EURUSD, GBPUSD, USDJPY, USDCHF
Commodity Pairs: AUDUSD, USDCAD, NZDUSD
Cross Pairs: EURGBP, EURJPY, GBPJPY, EURAUD, EURCAD, EURCHF, GBPCHF, GBPAUD
Others: AUDCAD, AUDCHF, AUDJPY, AUDNZD, CADJPY, CADCHF, CHFJPY, NZDJPY, NZDCAD, NZDCHF, GBPCAD, GBPNZD
Precious Metals: XAUUSD, XAGUSD
Others: USDRUB
```

Custom symbols can be added via the Web UI or CLI.

---

## Architecture

### Project Structure

```
dukascopy-downloader/
├── app.py                  # Main download orchestrator
├── cli.py                  # Command-line interface
├── server.py               # FastAPI web server
├── requirements.txt        # Python dependencies
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration and constants
├── core/
│   ├── __init__.py
│   ├── fetch.py            # Async tick data fetcher
│   ├── candle_fetch.py     # Native candle data fetcher
│   ├── processor.py        # LZMA decompression & tick parsing
│   ├── candle.py           # Candle aggregation class
│   ├── csv_dumper.py       # CSV file writer
│   └── validator.py        # Data validation
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Logging configuration
│   ├── progress.py         # Progress bar utilities
│   └── resume.py           # State persistence for resume
├── static/
│   └── index.html          # Web UI (single-page app)
├── tests/
│   ├── test_millisecond_precision.py
│   └── test_e2e_api.py
└── test_candle_urls.py     # URL discovery utility
```

### Data Flow

```
1. User Request (CLI/Web UI)
         ↓
2. Date Range Generation (skip Saturdays & today)
         ↓
3. For each day:
   ├── Fetch 24 hourly .bi5 files (async)
   ├── LZMA decompress each file
   ├── Parse binary tick data (20 bytes/tick)
   └── Normalize timestamps (UTC)
         ↓
4. Aggregate ticks → candles (if timeframe ≠ TICK)
         ↓
5. Write CSV output
         ↓
6. Validate data integrity
```

### Binary Data Format

#### Tick Data (20 bytes per tick)
```
struct.unpack('!IIIff', data)
- I: time offset (ms from hour start)
- I: ask price (integer, divide by point_value)
- I: bid price (integer, divide by point_value)
- f: ask volume (float, multiply by 1,000,000)
- f: bid volume (float, multiply by 1,000,000)
```

#### Candle Data (24 bytes per candle)
```
struct.unpack('!IIIIIf', data)
- I: time offset (seconds from base)
- I: open price
- I: close price
- I: low price
- I: high price
- f: volume
```

---

## Troubleshooting

### Common Issues

#### Server Won't Start

**Symptom:** Port 8000 is already in use.

**Solution:** The server automatically tries the next port (8001, 8002...). Check the terminal output for the actual port being used.

```bash
# Or manually kill the process using port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /F /PID <PID>
```

#### Mobile Can't Connect

**Symptom:** Phone can't access the web UI.

**Solutions:**
1. Ensure phone and PC are on the same WiFi network
2. Check Windows Firewall - allow Python on private networks
3. Try the IP address shown in the terminal (e.g., `http://192.168.1.5:8000`)

#### HTTP 503 Errors

**Symptom:** Downloads fail with rate limiting errors.

**Solutions:**
1. Reduce thread count (try `--threads 3`)
2. The tool has built-in exponential backoff; wait and retry
3. Avoid downloading during peak hours

#### Slow Downloads

**Symptom:** Downloads are slower than expected.

**Explanation:** This is intentional. The tool uses conservative settings to avoid rate limiting:
- Staggered requests
- Limited concurrent connections
- Retry delays

**To speed up (at your own risk):**
```bash
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1 --threads 10
```

#### Empty Output Files

**Symptom:** CSV file has no data rows.

**Possible Causes:**
1. Date range includes only weekends (Saturdays are skipped)
2. Today's data is not available yet
3. Symbol doesn't exist for that date range
4. All requests failed (check logs)

### Debug Mode

Enable verbose logging to see more details:

```python
# In utils/logger.py, change:
console_handler.setLevel(logging.DEBUG)
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/dukascopy-downloader.git
cd dukascopy-downloader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_e2e_api.py
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Disclaimer

This tool is for educational and research purposes. Dukascopy's data is provided for personal use. Please respect their terms of service and rate limits. The authors are not affiliated with Dukascopy Bank SA.

---

## Acknowledgments

- Inspired by the [duka](https://github.com/giuse88/duka) project
- Thanks to Dukascopy Bank SA for providing free historical data access

---

<p align="center">
  <strong>Made with ❤️ for the quantitative trading community</strong>
</p>
