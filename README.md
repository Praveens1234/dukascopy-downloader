# Dukascopy Historical Data Downloader

A production-ready tool to download high-quality historical tick and candle data from Dukascopy. Features both a robust **Command Line Interface (CLI)** for automation and a modern **Web UI** for ease of use.

![Web UI](https://via.placeholder.com/800x450.png?text=Web+UI+Preview)

## 🚀 Features

- **Dual Interface**: Choice of CLI for scripts/power users or Web UI for visual management.
- **Robust Downloading**:
  - **Anti-Rate-Limiting**: Browser emulation, exponential backoff, and request staggering to avoid 503 errors.
  - **Resumable**: Saves progress every 5 days; automatically resumes interrupted downloads.
  - **Correctness**: Validates data continuity, handles weekends/holidays, and normalizes prices.
- **Web UI**:
  - **Responsive Design**: Works perfectly on Desktop and Mobile.
  - **Live Monitoring**: Real-time progress bars and streaming terminal logs.
  - **Job Management**: Start, monitor, and cancel downloads.
  - **File Manager**: Browse, download, and delete exported CSV files.
- **CLI**:
  - **Batch Processing**: Download multiple symbols and year ranges in one go.
  - **Flexible Output**: Tick data or aggregated candles (M1, H1, D1, etc.).

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

The Web UI is the easiest way to use the downloader.

1.  **Start the Server**:
    ```bash
    python server.py
    ```
    *   The browser will open automatically at `http://localhost:8000`.
    *   **Mobile Access**: The terminal will display a network URL (e.g., `http://192.168.1.5:8000`). Open this on your phone while on the same WiFi.

2.  **Start a Download**:
    *   Go to **New Download**.
    *   Select **Symbols** (click chips or type custom ones like `BTCUSD`).
    *   Choose **Date Range** and **Timeframe** (Tick, M1, H1, etc.).
    *   Adjust **Threads** slider (default 5 is safe).
    *   Click **Start Download**.

3.  **Monitor & Manage**:
    *   Watch progress in the active panel.
    *   View detailed logs in the **Terminal** tab.
    *   Click **Stop 🛑** to cancel a running job.
    *   Go to **Files** tab to download your CSVs.

## 💻 CLI Usage

For automation or headless environments.

**Basic Download**:
```bash
python cli.py EURUSD -s 2023-01-01 -e 2023-12-31 -t M1
```

**Multiple Symbols & Timeframes**:
```bash
python cli.py EURUSD GBPUSD XAUUSD -s 2024-01-01 -e 2024-06-01 -t H1
```

**Resume an Interrupted Download**:
```bash
python cli.py EURUSD -s 2020-01-01 -e 2024-01-01 --resume
```

**Options**:
- `-s, --start`: Start date (YYYY-MM-DD).
- `-e, --end`: End date (YYYY-MM-DD).
- `-t, --timeframe`: `TICK` (default), `M1`, `M5`, `M15`, `M30`, `H1`, `H4`, `D1`.
- `--threads`: Number of download threads (default: 5).
- `--resume`: Resume from last saved state.
- `--help`: Show all options.

## 📂 Output

Files are saved to the `data/` directory in CSV format:
`{SYMBOL}_{TIMEFRAME}_{START}_{END}.csv`

**Format (Candles)**:
`timestamp,open,high,low,close,volume`

**Format (Ticks)**:
`timestamp,ask,bid,ask_vol,bid_vol`

## ⚙️ Configuration

Settings can be tweaked in `config/settings.py` if needed (e.g., modifying retry delays or concurrency limits), but the defaults are tuned for stability.

## ❓ Troubleshooting

*   **Server won't start?**
    *   It tries port 8000. If busy, it will try 8001, etc. Check the terminal output.
*   **Mobile can't connect?**
    *   Ensure phone and PC are on the same WiFi.
    *   Check if Windows Firewall is blocking Python. Allow access to private networks.
*   **Download stuck/slow?**
    *   Dukascopy limits download speed. We use 5 threads to be polite. Increasing threads >10 may cause blocking (HTTP 503).

## 📄 License
MIT License
