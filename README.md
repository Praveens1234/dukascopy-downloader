# Dukascopy Historical Data Downloader

A high-performance, production-ready tool to download high-quality historical tick and candle data from Dukascopy.
Engineered for reliability, speed, and data integrity.

![Web UI](https://via.placeholder.com/800x450.png?text=Web+UI+Preview)

## 🚀 Key Features

### 🛡️ Robust & Resilient
-   **Streaming Architecture**: Processes data chunk-by-chunk using a Map-Reduce approach. Can handle 10+ years of tick data without OOM crashes (constant low memory footprint).
-   **Smart Resume**: Tracks progress daily. If interrupted, resumes exactly where it left off.
-   **Holiday Awareness**: Automatically skips global market holidays (Jan 1, Dec 25) to save time and bandwidth.
-   **Circuit Breaker**: Detects repeated `503 Service Unavailable` errors and automatically backs off for 60s to avoid IP bans.

### 🎯 Accurate Data
-   **Midnight Crossing Fix**: Correctly aggregates candles that span across daily boundaries (e.g., `4H`, `7H`) using a sophisticated merging algorithm.
-   **Strict Validation**: Checks for gaps, duplicates, zero-prices, and OHLC consistency.
-   **Precision**: Uses decimal-correct rounding to prevent floating-point drift.

### ⚡ Performance
-   **Async I/O**: Uses `aiohttp` with connection pooling, DNS caching, and exponential backoff.
-   **Parallel Downloads**: Multi-threaded downloading of days, fully configurable.

## 🛠️ Installation

1.  **Prerequisites**: Python 3.8 or higher.
2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/Praveens1234/dukascopy-downloader.git
    cd dukascopy-downloader
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🖥️ Web UI Usage

1.  **Start the Server**:
    ```bash
    python server.py
    ```
    *   Open `http://localhost:8000`.
    *   **Mobile**: Access via the LAN IP displayed in the terminal.

2.  **Features**:
    *   **Live Logs**: Real-time streaming logs via WebSockets.
    *   **Progress Tracking**: Visual progress bars.
    *   **File Manager**: Download/Delete generated CSVs directly.

## 💻 CLI Usage

For automation or headless servers.

```bash
# Basic Download (Tick Data)
python cli.py EURUSD -s 2023-01-01 -e 2023-01-31

# Candle Download (1 Minute)
python cli.py GBPUSD -s 2023-01-01 -e 2023-12-31 -t M1

# Custom Timeframe (e.g., 2 Hours)
python cli.py XAUUSD -s 2023-01-01 -e 2023-06-01 -t CUSTOM --custom-tf 2h

# Resume Interrupted Download
python cli.py EURUSD -s 2020-01-01 -e 2024-01-01 --resume
```

**Options**:
- `-s, --start`: Start date (YYYY-MM-DD).
- `-e, --end`: End date (YYYY-MM-DD).
- `-t, --timeframe`: `TICK` (default), `M1`, `H1`, `D1`, `CUSTOM`.
- `--custom-tf`: Seconds (`120`) or suffix (`10s`, `2h`).
- `--threads`: Parallel threads (default 5).
- `--source`: `auto` (default), `native` (fastest for M1/H1/D1), `tick` (most accurate).

## 🧪 Testing

The project includes a comprehensive test suite using `pytest`.

```bash
# Run all tests
pytest

# Run end-to-end system tests
pytest tests/e2e_cli.py tests/e2e_server.py
```

## ⚙️ Configuration

Defaults can be tweaked in `config/settings.py`.
Key settings:
-   `HOURLY_CONCURRENCY`: Max async requests per day (default 8).
-   `DOWNLOAD_ATTEMPTS`: Max retries per file (default 10).
-   `HTTP_TIMEOUT`: Request timeout (default 60s).

## 📄 License
MIT License
