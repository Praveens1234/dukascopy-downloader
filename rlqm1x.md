<div align="center">

# 🌟 Dukascopy Historical Data Downloader 🌟

<img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"/>
<img src="https://img.shields.io/badge/FastAPI-0.104%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge" alt="Platform"/>
<img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge" alt="Status"/>

### 🚀 *The Most Advanced & Production-Ready Tool for Downloading Historical Forex & CFD Data from Dukascopy Bank SA* 🚀

<p>
  <b>🔥 Dual Interface</b> • <b>⚡ Lightning Fast</b> • <b>🛡️ Anti-Rate-Limiting</b> • <b>📦 Resumable Downloads</b> • <b>✨ Millisecond Precision</b>
</p>

---

<img src="https://user-images.githubusercontent.com/74038190/225811702-68b3a3d3-9d9f-4e6e-a3d6-3c3d3e3e3e3e.gif" width="400"/>

</div>

---

## 📑 Table of Contents

| 📌 Section | 🎯 Description |
|:----------:|:--------------:|
| [🎬 Introduction](#-introduction) | What is this tool & why use it? |
| [✨ Features](#-features) | Complete feature breakdown |
| [🏗️ Architecture](#️-architecture) | Project structure & design |
| [📦 Installation](#-installation) | Quick setup guide |
| [🎯 Quick Start](#-quick-start) | Get started in 30 seconds |
| [🌐 Web UI Guide](#-web-ui-guide) | Full web interface documentation |
| [💻 CLI Reference](#-cli-reference) | Complete command-line documentation |
| [🔌 API Reference](#-api-reference) | REST API & WebSocket docs |
| [📊 Output Format](#-output-format) | CSV structure & examples |
| [⚙️ Configuration](#️-configuration) | All configurable settings |
| [🔧 Advanced Usage](#-advanced-usage) | Custom timeframes & more |
| [📈 Data Flow](#-data-flow) | How data is processed |
| [🔍 Binary Format](#-binary-format) | Technical data specifications |
| [❓ Troubleshooting](#-troubleshooting) | Common issues & solutions |
| [🤝 Contributing](#-contributing) | How to contribute |
| [📄 License](#-license) | MIT License |

---

<div align="center">

## 🎬 Introduction

</div>

> ### 💡 What is Dukascopy Historical Data Downloader?

**Dukascopy Historical Data Downloader** is a **production-grade**, **enterprise-ready** Python application designed to reliably download high-quality historical **tick** and **OHLC candle** data from Dukascopy Bank's free datafeed. It's the **most comprehensive** and **feature-rich** solution available for forex data acquisition.

<br>

<table>
<tr>
<td width="50%">

### 🎯 Why This Tool Exists

Dukascopy Bank provides **free access** to premium-quality forex data, but downloading it reliably is **extremely challenging**:

</td>
<td width="50%">

### ✅ Our Solution

This tool addresses **every single challenge** with production-ready implementations:

</td>
</tr>
<tr>
<td>

| 🚫 Problem | 😫 Impact |
|:----------:|:---------:|
| **Rate Limiting** | HTTP 503 errors blocking downloads |
| **Binary Format** | .bi5 files need LZMA decompression |
| **Time Precision** | Millisecond timestamps across timezones |
| **Data Integrity** | Gaps, duplicates, ordering issues |
| **Resume Capability** | Large downloads fail mid-way |

</td>
<td>

| ✨ Feature | 🎁 Benefit |
|:----------:|:----------:|
| **Smart Backoff** | Exponential + jitter algorithm |
| **Binary Parser** | Handles 20-byte tick structs |
| **UTC-Safe** | Proper timezone bucketing |
| **Validation** | Auto-checks chronological order |
| **State Saving** | Resume from last checkpoint |

</td>
</tr>
</table>

<br>

<div align="center">

### 🏆 Key Differentiators

</div>

| 🔥 Feature | 📝 Description | 🎯 Advantage |
|:----------:|:--------------|:------------:|
| **Dual Interface** | Modern Web UI + Powerful CLI | Use however you prefer |
| **Native Candles** | Direct M1/H1/D1 from Dukascopy | 10x faster than tick conversion |
| **Tick-to-Candle** | Convert ticks to any timeframe | Unlimited flexibility |
| **Anti-Rate-Limit** | Browser emulation + smart delays | No 503 errors |
| **WebSocket Logs** | Real-time streaming updates | Live monitoring |
| **Crash Recovery** | State saved every 5 days | Never lose progress |
| **Custom Symbols** | Add any symbol you want | BTCUSD, ETHUSD, etc. |
| **Price Types** | BID, ASK, or MID prices | Complete market view |
| **Volume Types** | Total, BID, ASK, or tick count | Flexible analysis |

---

<div align="center">

## ✨ Features

</div>

### 📊 Data Acquisition Capabilities

<div align="center">

| 🎯 Data Type | 📏 Precision | 📦 Source | ⚡ Speed |
|:------------:|:------------:|:---------:|:--------:|
| **Raw Ticks** | Millisecond | 24 hourly files/day | Standard |
| **M1 Candles** | Second | Native or Tick-derived | Fast/Standard |
| **H1 Candles** | Second | Native or Tick-derived | Fast/Standard |
| **D1 Candles** | Second | Native or Tick-derived | Fast/Standard |
| **Custom TF** | Second | Tick-derived | Standard |

</div>

<details>
<summary><b>🔬 Detailed Feature Breakdown</b></summary>

#### 🌐 Web Interface Features

| Feature | Description |
|---------|-------------|
| 🎨 **Responsive Design** | Works flawlessly on Desktop, Tablet, and Mobile |
| 📡 **Real-time Updates** | WebSocket-powered live progress and logs |
| 📋 **Job Management** | Start, monitor, pause, and cancel downloads |
| 📁 **File Manager** | Browse, download, and delete CSV files |
| 🔧 **Custom Symbols** | Add any symbol beyond the predefined list |
| 🌙 **Modern UI** | Dark theme with gradient accents |

#### 💻 CLI Features

| Feature | Description |
|---------|-------------|
| 🔄 **Batch Processing** | Download multiple symbols in one command |
| 📊 **Progress Bars** | Beautiful tqdm-powered progress display |
| 💾 **Resume Support** | Continue interrupted downloads |
| 🎯 **Flexible Output** | Custom directories, header options |
| 🤖 **Automation Ready** | Perfect for cron jobs and scripts |

#### 🛡️ Reliability Features

| Feature | Description |
|---------|-------------|
| 🔁 **10 Retry Attempts** | Exponential backoff with random jitter |
| 🕐 **60s Timeout** | Generous timeout per request |
| 🧵 **Thread Staggering** | Prevent burst requests |
| 💾 **State Persistence** | Resume state saved every 5 days |
| ✅ **Data Validation** | Post-download integrity checks |

</details>

---

<div align="center">

## 🏗️ Architecture

</div>

```
dukascopy-downloader/
│
├── 📄 app.py                 ⬅️ Main orchestrator (fetch → decompress → aggregate → dump)
├── 📄 cli.py                 ⬅️ Command-line interface with Click
├── 📄 server.py              ⬅️ FastAPI web server + WebSocket
├── 📄 requirements.txt       ⬅️ Python dependencies
│
├── 📂 config/
│   ├── __init__.py
│   └── 📄 settings.py        ⬅️ All configurable constants & URL templates
│
├── 📂 core/
│   ├── __init__.py
│   ├── 📄 fetch.py           ⬅️ Async tick data fetcher with anti-rate-limit
│   ├── 📄 candle_fetch.py    ⬅️ Native candle data fetcher (M1, H1, D1)
│   ├── 📄 processor.py       ⬅️ LZMA decompression & binary tick parsing
│   ├── 📄 candle.py          ⬅️ Candle aggregation class (OHLC)
│   ├── 📄 csv_dumper.py      ⬅️ CSV writer with price/volume type support
│   └── 📄 validator.py       ⬅️ Post-download data validation
│
├── 📂 utils/
│   ├── __init__.py
│   ├── 📄 logger.py          ⬅️ Console + file logging
│   ├── 📄 progress.py        ⬅️ TQDM progress bars
│   └── 📄 resume.py          ⬅️ State persistence for crash recovery
│
├── 📂 static/
│   └── 📄 index.html         ⬅️ Single-page Web UI (900+ lines)
│
└── 📂 tests/
    ├── test_millisecond_precision.py
    └── test_e2e_api.py
```

---

<div align="center">

## 📦 Installation

</div>

### 📋 Prerequisites

| Requirement | Version | Purpose |
|:------------|:-------:|:--------|
| Python | ≥ 3.8 | Runtime environment |
| pip | Latest | Package manager |
| Git | Latest | Clone repository |

### 🚀 Quick Install

```bash
# 1️⃣ Clone the repository
git clone https://github.com/Praveens1234/dukascopy-downloader.git

# 2️⃣ Navigate to project
cd dukascopy-downloader

# 3️⃣ Install dependencies
pip install -r requirements.txt

# ✅ Done! Start downloading data!
```

### 📦 Dependencies

| Package | Version | Purpose |
|---------|:-------:|---------|
| `aiohttp` | ≥ 3.8.0 | Async HTTP client for downloading |
| `tqdm` | ≥ 4.64.0 | Beautiful progress bars |
| `click` | ≥ 8.0.0 | CLI argument parsing |
| `fastapi` | ≥ 0.104.0 | Web server framework |
| `uvicorn[standard]` | ≥ 0.24.0 | ASGI server |
| `python-multipart` | ≥ 0.0.6 | Form data parsing |

---

<div align="center">

## 🎯 Quick Start

</div>

<table>
<tr>
<td width="50%" align="center">

### 🌐 Option 1: Web UI (Recommended)

```bash
python server.py
```

✅ Browser opens automatically
✅ Mobile-friendly interface
✅ Real-time progress & logs

</td>
<td width="50%" align="center">

### 💻 Option 2: CLI (Automation)

```bash
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1
```

✅ Perfect for scripts
✅ Batch processing
✅ Resumable downloads

</td>
</tr>
</table>

---

<div align="center">

## 🌐 Web UI Guide

</div>

### 🎨 Interface Overview

<div align="center">

| Tab | Purpose |
|:---:|:--------|
| 📥 **New Download** | Configure and start new downloads |
| 📋 **Jobs** | View all download job history |
| 📁 **Files** | Browse, download, delete CSV files |
| ⌨️ **Terminal** | Live streaming logs via WebSocket |

</div>

### 📝 Configuration Options

#### 1️⃣ Symbols Selection

```
┌─────────────────────────────────────────────────────────────┐
│  Predefined Symbols (Click to select)                       │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐    │
│  │EURUSD│ │GBPUSD│ │USDJPY│ │XAUUSD│ │XAGUSD│ │AUDUSD│    │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘ └──────┘    │
│                                                             │
│  Custom Symbols: [Type BTCUSD, ETHUSD, etc.]  [+ Add]      │
└─────────────────────────────────────────────────────────────┘
```

#### 2️⃣ Date & Timeframe

| Field | Format | Example |
|-------|--------|---------|
| Start Date | YYYY-MM-DD | 2024-01-01 |
| End Date | YYYY-MM-DD | 2024-12-31 |
| Timeframe | Dropdown | M1, H1, D1, TICK, etc. |

#### 3️⃣ Data Source Options

| Option | Behavior | Best For |
|--------|----------|----------|
| **Auto** ✨ | Native if available, else tick | Most users |
| **Tick → Candle** | Always convert ticks | Custom timeframes |
| **Native OHLC** | Direct from Dukascopy | M1, H1, D1 only |

#### 4️⃣ Price & Volume Types

| Type | Options | Description |
|------|---------|-------------|
| **Price Type** | BID, ASK, MID | Price calculation method |
| **Volume Type** | TOTAL, BID, ASK, TICKS | Volume aggregation method |

---

<div align="center">

## 💻 CLI Reference

</div>

### 📝 Basic Syntax

```bash
python cli.py SYMBOLS -s START_DATE -e END_DATE [OPTIONS]
```

### 🔧 Required Arguments

| Argument | Short | Format | Description |
|----------|-------|--------|-------------|
| `SYMBOLS` | - | `EURUSD GBPUSD` | One or more currency pairs |
| `--start` | `-s` | `YYYY-MM-DD` | Start date |
| `--end` | `-e` | `YYYY-MM-DD` | End date |

### ⚙️ Optional Arguments

| Argument | Short | Default | Description |
|----------|-------|---------|-------------|
| `--timeframe` | `-t` | `TICK` | Data timeframe |
| `--custom-tf` | - | - | Custom timeframe (e.g., `5m`, `2h`) |
| `--threads` | - | `5` | Parallel download threads |
| `--output` | `-o` | `.` | Output directory |
| `--header` | - | `True` | Include CSV header |
| `--resume` | - | `False` | Resume interrupted download |
| `--source` | - | `auto` | Data source selection |
| `--price-type` | - | `BID` | Price type |
| `--volume-type` | - | `TOTAL` | Volume type |

### 📊 Supported Timeframes

<div align="center">

| Category | Timeframes | Native Support |
|:--------:|:-----------|:--------------:|
| 🔴 **Tick** | `TICK` | ❌ |
| 🟠 **Seconds** | `S1`, `S10`, `S30` | ❌ |
| 🟡 **Minutes** | `M1`, `M2`, `M3`, `M4`, `M5`, `M10`, `M15`, `M30` | ✅ M1 only |
| 🟢 **Hours** | `H1`, `H4` | ✅ H1 only |
| 🔵 **Days** | `D1` | ✅ D1 |
| 🟣 **Custom** | `CUSTOM` + `--custom-tf` | ❌ |

</div>

### 📚 CLI Examples

<details>
<summary><b>🔹 Basic Examples</b></summary>

```bash
# Download raw tick data (highest precision)
python cli.py EURUSD -s 2024-01-01 -e 2024-01-02 -t TICK

# Download minute candles
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1

# Download multiple symbols
python cli.py EURUSD GBPUSD XAUUSD -s 2024-01-01 -e 2024-06-01 -t H1

# Download daily candles
python cli.py XAUUSD -s 2020-01-01 -e 2024-12-31 -t D1
```

</details>

<details>
<summary><b>🔹 Advanced Examples</b></summary>

```bash
# Use native candles (faster for M1, H1, D1)
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1 --source native

# Resume interrupted download
python cli.py EURUSD -s 2020-01-01 -e 2024-12-31 --resume

# Custom timeframe (2-hour candles)
python cli.py EURUSD -s 2024-01-01 -e 2024-06-01 -t CUSTOM --custom-tf 2h

# Custom timeframe in seconds (90-second candles)
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 90

# Custom timeframe in minutes
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 5m

# Specific price and volume types
python cli.py XAUUSD -s 2024-01-01 -e 2024-12-31 -t H1 \
    --price-type ASK --volume-type TICKS

# Increase threads (use cautiously)
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1 --threads 10

# Custom output directory
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1 -o ./my_data

# No header in CSV
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t M1 --no-header
```

</details>

---

<div align="center">

## 🔌 API Reference

</div>

### 🌐 REST API Endpoints

<table>
<tr>
<th>Method</th>
<th>Endpoint</th>
<th>Description</th>
</tr>
<tr>
<td><code>GET</code></td>
<td><code>/api/config</code></td>
<td>Get available symbols, timeframes, and defaults</td>
</tr>
<tr>
<td><code>POST</code></td>
<td><code>/api/download</code></td>
<td>Start a new download job</td>
</tr>
<tr>
<td><code>GET</code></td>
<td><code>/api/jobs</code></td>
<td>List all jobs (most recent first)</td>
</tr>
<tr>
<td><code>GET</code></td>
<td><code>/api/jobs/{job_id}</code></td>
<td>Get job status and logs</td>
</tr>
<tr>
<td><code>POST</code></td>
<td><code>/api/jobs/{job_id}/cancel</code></td>
<td>Cancel a running job</td>
</tr>
<tr>
<td><code>GET</code></td>
<td><code>/api/files</code></td>
<td>List all CSV files</td>
</tr>
<tr>
<td><code>GET</code></td>
<td><code>/api/files/{filename}</code></td>
<td>Download a CSV file</td>
</tr>
<tr>
<td><code>DELETE</code></td>
<td><code>/api/files/{filename}</code></td>
<td>Delete a CSV file</td>
</tr>
</table>

### 📡 WebSocket Endpoint

```
ws://localhost:8000/ws
```

**Message Types:**

```json
// Log message
{"type": "log", "job_id": "abc123", "message": "[10:30:15] Downloading EURUSD..."}

// Progress update
{"type": "progress", "job_id": "abc123", "status": "running", "progress": 45.5, "completed_days": 166, "total_days": 365}
```

### 📋 Request/Response Examples

<details>
<summary><b>GET /api/config</b></summary>

**Response:**
```json
{
  "symbols": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", ...],
  "timeframes": ["TICK", "S1", "S10", "S30", "M1", "M2", "M3", "M4", "M5", "M10", "M15", "M30", "H1", "H4", "D1", "CUSTOM"],
  "default_threads": 5,
  "max_threads": 30,
  "volume_types": ["TOTAL", "BID", "ASK", "TICKS"]
}
```

</details>

<details>
<summary><b>POST /api/download</b></summary>

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

</details>

<details>
<summary><b>GET /api/jobs/{job_id}</b></summary>

**Response:**
```json
{
  "id": "a1b2c3d4",
  "status": "running",
  "params": {
    "symbols": ["EURUSD"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  },
  "progress": 45.5,
  "total_days": 365,
  "completed_days": 166,
  "logs": [
    "[10:30:00] Starting download: EURUSD",
    "[10:30:01] Date range: 2024-01-01 to 2024-12-31 | Timeframe: M1"
  ],
  "started_at": "2024-01-15T10:30:00",
  "finished_at": null,
  "output_file": null,
  "error": null
}
```

</details>

---

<div align="center">

## 📊 Output Format

</div>

### 📁 File Naming Convention

```
{SYMBOL}-{START_YEAR}_{START_MONTH}_{START_DAY}-{END_YEAR}_{END_MONTH}_{END_DAY}.csv
```

**Example:** `EURUSD-2024_01_01-2024_12_31.csv`

### 📝 CSV Formats

#### 🔴 Tick Data Format

| Column | Type | Description |
|--------|------|-------------|
| `time` | String | `DD.MM.YYYY HH:MM:SS.mmm` (UTC) |
| `ask` | Float | Ask price (5 decimals) |
| `bid` | Float | Bid price (5 decimals) |
| `ask_volume` | Integer | Ask volume in lots |
| `bid_volume` | Integer | Bid volume in lots |

**Example:**
```csv
time,ask,bid,ask_volume,bid_volume
01.01.2024 00:00:00.123,1.10425,1.10420,150,200
01.01.2024 00:00:00.456,1.10430,1.10425,100,150
01.01.2024 00:00:00.789,1.10428,1.10423,75,125
```

#### 🟢 Candle Data Format (OHLCV)

| Column | Type | Description |
|--------|------|-------------|
| `time` | String | `DD.MM.YYYY HH:MM:SS` (UTC) |
| `open` | Float | Opening price (5 decimals) |
| `high` | Float | Highest price (5 decimals) |
| `low` | Float | Lowest price (5 decimals) |
| `close` | Float | Closing price (5 decimals) |
| `volume` | Float | Volume (based on volume_type) |

**Example:**
```csv
time,open,high,low,close,volume
01.01.2024 00:00:00,1.10420,1.10435,1.10415,1.10430,1250.5
01.01.2024 00:01:00,1.10430,1.10445,1.10425,1.10440,980.25
01.01.2024 00:02:00,1.10440,1.10450,1.10435,1.10448,756.75
```

---

<div align="center">

## ⚙️ Configuration

</div>

### 📋 All Configurable Settings (`config/settings.py`)

<details>
<summary><b>🌐 URL Templates</b></summary>

```python
# Tick data URL (24 hourly files per day)
URL_TEMPLATE = "https://www.dukascopy.com/datafeed/{currency}/{year}/{month:02d}/{day:02d}/{hour:02d}h_ticks.bi5"

# Native candle URLs (pre-computed OHLC)
CANDLE_URL_TEMPLATES = {
    'M1': ".../{currency}/{year}/{month:02d}/{day:02d}/{price_type}_candles_min_1.bi5",
    'H1': ".../{currency}/{year}/{month:02d}/{price_type}_candles_hour_1.bi5",
    'D1': ".../{currency}/{year}/{price_type}_candles_day_1.bi5",
}
```

</details>

<details>
<summary><b>⬇️ Download Settings</b></summary>

| Setting | Value | Purpose |
|---------|-------|---------|
| `DEFAULT_THREADS` | `5` | Safe default to avoid rate limits |
| `MAX_THREADS` | `30` | Maximum allowed threads |
| `DOWNLOAD_ATTEMPTS` | `10` | Retries before giving up |
| `RETRY_BASE_DELAY` | `1.0s` | Base delay for backoff |
| `RETRY_MAX_DELAY` | `30.0s` | Maximum delay between retries |
| `HOURLY_CONCURRENCY` | `8` | Max concurrent hourly downloads |
| `REQUEST_DELAY` | `0.1s` | Delay between request starts |
| `HTTP_TIMEOUT` | `60s` | Timeout per request |

</details>

<details>
<summary><b>📊 Timeframe Definitions</b></summary>

```python
class TimeFrame:
    TICK = 0        # Raw tick data
    S1   = 1        # 1 second
    S10  = 10       # 10 seconds
    S30  = 30       # 30 seconds
    M1   = 60       # 1 minute
    M2   = 120      # 2 minutes
    M3   = 180      # 3 minutes
    M4   = 240      # 4 minutes
    M5   = 300      # 5 minutes
    M10  = 600      # 10 minutes
    M15  = 900      # 15 minutes
    M30  = 1800     # 30 minutes
    H1   = 3600     # 1 hour
    H4   = 14400    # 4 hours
    D1   = 86400    # 1 day
```

</details>

<details>
<summary><b>💱 Supported Symbols</b></summary>

| Category | Symbols |
|----------|---------|
| **Major Pairs** | EURUSD, GBPUSD, USDJPY, USDCHF |
| **Commodity Pairs** | AUDUSD, USDCAD, NZDUSD |
| **Cross Pairs** | EURGBP, EURJPY, GBPJPY, EURAUD, EURCAD, EURCHF, GBPCHF, GBPAUD |
| **Others** | AUDCAD, AUDCHF, AUDJPY, AUDNZD, CADJPY, CADCHF, CHFJPY, NZDJPY, NZDCAD, NZDCHF, GBPCAD, GBPNZD |
| **Precious Metals** | XAUUSD (Gold), XAGUSD (Silver) |
| **Others** | USDRUB |

**Note:** Custom symbols can be added via Web UI or CLI!

</details>

<details>
<summary><b>🔢 Special Point Values</b></summary>

```python
# Some symbols have different price precision
SPECIAL_POINT_SYMBOLS = {
    'usdrub': 1000,    # Russian Ruble
    'xagusd': 1000,    # Silver
    'xauusd': 1000,    # Gold
    'xaugbp': 1000,    # Gold in GBP
    'xaueur': 1000,    # Gold in EUR
    'xageur': 1000,    # Silver in EUR
    'xaggbp': 1000,    # Silver in GBP
}
DEFAULT_POINT_VALUE = 100000  # Standard forex pairs
VOLUME_MULTIPLIER = 1_000_000  # Volume scaling
```

</details>

---

<div align="center">

## 🔧 Advanced Usage

</div>

### 🎯 Custom Timeframes

The tool supports **any custom timeframe** via the `CUSTOM` option:

```bash
# Using seconds directly
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 90

# Using suffixed notation
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 30s   # 30 seconds
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 5m    # 5 minutes
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 2h    # 2 hours
python cli.py EURUSD -s 2024-01-01 -e 2024-01-31 -t CUSTOM --custom-tf 1d    # 1 day
```

### 🔄 Resume Interrupted Downloads

Large downloads can be interrupted. Resume them easily:

```bash
# Original command that was interrupted
python cli.py EURUSD -s 2020-01-01 -e 2024-12-31 -t M1 --resume
```

**How it works:**
- State is saved every 5 days to `.download_state.json`
- Resume skips already-completed dates
- State is cleared on successful completion

### 🧵 Threading Optimization

| Threads | Use Case | Risk Level |
|---------|----------|------------|
| `1-3` | Very conservative, unstable connections | 🟢 Safe |
| `5` | Default, recommended for most users | 🟢 Safe |
| `10-15` | Faster downloads, good connection | 🟡 Moderate |
| `20-30` | Maximum speed, may trigger rate limits | 🔴 Risky |

---

<div align="center">

## 📈 Data Flow

</div>

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW PIPELINE                              │
└─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐
  │ User Request │  ◀── CLI or Web UI
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐      ┌───────────────────────────────────┐
  │ Generate Days│ ───▶ │ Skip Saturdays & Today            │
  └──────┬───────┘      │ Generate trading days only        │
         │              └───────────────────────────────────┘
         ▼
  ┌──────────────┐
  │ For Each Day │ ◀─────────────────────────────────────────────┐
  └──────┬───────┘                                               │
         │                                                       │
         ▼                                                       │
  ┌──────────────┐      ┌───────────────────────────────────┐   │
  │ Fetch 24     │ ───▶ │ https://dukascopy.com/datafeed/   │   │
  │ Hourly Files │      │ {symbol}/{year}/{month}/{day}/    │   │
  └──────┬───────┘      │ {hour}h_ticks.bi5                 │   │
         │              └───────────────────────────────────┘   │
         ▼                                                       │
  ┌──────────────┐      ┌───────────────────────────────────┐   │
  │ LZMA         │ ───▶ │ Decompress .bi5 files             │   │
  │ Decompress   │      │ Handle multiple streams           │   │
  └──────┬───────┘      └───────────────────────────────────┘   │
         │                                                       │
         ▼                                                       │
  ┌──────────────┐      ┌───────────────────────────────────┐   │
  │ Parse Binary │ ───▶ │ 20 bytes per tick                 │   │
  │ Ticks        │      │ struct.unpack('!IIIff')           │   │
  └──────┬───────┘      └───────────────────────────────────┘   │
         │                                                       │
         ▼                                                       │
  ┌──────────────┐      ┌───────────────────────────────────┐   │
  │ Normalize    │ ───▶ │ Convert to datetime + prices      │   │
  │ Timestamps   │      │ Apply point_value & volume_mult   │   │
  └──────┬───────┘      └───────────────────────────────────┘   │
         │                                                       │
         ▼                                                       │
  ┌──────────────┐                                              │
  │ Aggregate to │ ───▶ Skip if TICK timeframe                  │
  │ Candles?     │                                              │
  └──────┬───────┘                                              │
         │                                                       │
         ▼                                                       │
  ┌──────────────┐                                              │
  │ Buffer Data  │ ─────────────────────────────────────────────┘
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Write CSV    │      Format: DD.MM.YYYY HH:MM:SS
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Validate     │      Check: row count, chronology, price range
  └──────────────┘
```

---

<div align="center">

## 🔍 Binary Format

</div>

### 📦 Tick Data Structure (20 bytes)

```
┌─────────────────────────────────────────────────────────────────┐
│                    TICK BINARY FORMAT                           │
├─────────┬─────────┬─────────────────────────────────────────────┤
│ Offset  │ Size    │ Description                                 │
├─────────┼─────────┼─────────────────────────────────────────────┤
│ 0-3     │ 4 bytes │ Time offset (ms from hour start)           │
│ 4-7     │ 4 bytes │ Ask price (÷ point_value)                  │
│ 8-11    │ 4 bytes │ Bid price (÷ point_value)                  │
│ 12-15   │ 4 bytes │ Ask volume (× 1,000,000)                   │
│ 16-19   │ 4 bytes │ Bid volume (× 1,000,000)                   │
└─────────┴─────────┴─────────────────────────────────────────────┘

Python: struct.unpack('!IIIff', data)
```

### 🕯️ Candle Data Structure (24 bytes)

```
┌─────────────────────────────────────────────────────────────────┐
│                   CANDLE BINARY FORMAT                          │
├─────────┬─────────┬─────────────────────────────────────────────┤
│ Offset  │ Size    │ Description                                 │
├─────────┼─────────┼─────────────────────────────────────────────┤
│ 0-3     │ 4 bytes │ Time offset (seconds from base)            │
│ 4-7     │ 4 bytes │ Open price (÷ point_value)                 │
│ 8-11    │ 4 bytes │ Close price (÷ point_value)                │
│ 12-15   │ 4 bytes │ Low price (÷ point_value)                  │
│ 16-19   │ 4 bytes │ High price (÷ point_value)                 │
│ 20-23   │ 4 bytes │ Volume (float32)                           │
└─────────┴─────────┴─────────────────────────────────────────────┘

Python: struct.unpack('!IIIIIf', data)
```

---

<div align="center">

## ❓ Troubleshooting

</div>

<details>
<summary><b>🔴 Server Won't Start</b></summary>

**Symptom:** Port 8000 is already in use.

**Solutions:**

```bash
# Method 1: Let server auto-try next port
# Just wait - it will try 8001, 8002, etc.

# Method 2: Kill process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /F /PID <PID>

# Method 3: Kill process on port 8000 (Linux/Mac)
lsof -i :8000
kill -9 <PID>
```

</details>

<details>
<summary><b>📱 Mobile Can't Connect</b></summary>

**Symptom:** Phone can't access the web UI.

**Solutions:**

1. ✅ Ensure phone and PC are on the **same WiFi network**
2. ✅ Check Windows Firewall → Allow Python on **Private networks**
3. ✅ Use the IP shown in terminal (e.g., `http://192.168.1.5:8000`)
4. ✅ Disable VPN on phone if active

</details>

<details>
<summary><b>⚡ HTTP 503 Errors</b></summary>

**Symptom:** Downloads fail with rate limiting errors.

**Solutions:**

```bash
# Reduce thread count
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1 --threads 3

# The tool has built-in exponential backoff
# Just wait and retry - it will succeed eventually
```

**Technical Details:**
- Dukascopy limits ~100 requests per minute per IP
- Our tool uses: 5 threads × 24 hours = 120 requests/day-symbol
- With staggering and delays, we stay well under limits

</details>

<details>
<summary><b>🐢 Slow Downloads</b></summary>

**Symptom:** Downloads seem slower than expected.

**Explanation:** This is **intentional** to avoid rate limits:
- Staggered requests (0.1s delay)
- Limited concurrency (5 threads)
- Retry delays (1-30 seconds)

**To speed up (at your own risk):**

```bash
# Increase threads cautiously
python cli.py EURUSD -s 2024-01-01 -e 2024-12-31 -t M1 --threads 15
```

</details>

<details>
<summary><b>📭 Empty Output Files</b></summary>

**Symptom:** CSV file has no data rows.

**Possible Causes & Solutions:**

| Cause | Solution |
|-------|----------|
| Date range is weekends | Saturdays are skipped automatically |
| Today's data not available | Exclude today from date range |
| Symbol doesn't exist | Verify symbol name |
| All requests failed | Check terminal for errors |

</details>

---

<div align="center">

## 🤝 Contributing

</div>

Contributions are welcome! Here's how to get started:

### 🔧 Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/dukascopy-downloader.git
cd dukascopy-downloader

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run tests
python tests/test_e2e_api.py
```

### 📋 Contribution Guidelines

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 📝 Open a Pull Request

---

<div align="center">

## 📄 License

</div>

```
MIT License

Copyright (c) 2024 Dukascopy Downloader

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<div align="center">

## ⚠️ Disclaimer

This tool is for **educational and research purposes only**. 

Dukascopy's data is provided for **personal use**. Please respect their terms of service and rate limits.

The authors are **not affiliated** with Dukascopy Bank SA.

---

## 🙏 Acknowledgments

| Project | Contribution |
|---------|--------------|
| [duka](https://github.com/giuse88/duka) | Original inspiration |
| [Dukascopy Bank SA](https://www.dukascopy.com) | Free historical data access |

---

<img src="https://user-images.githubusercontent.com/74038190/212284100-561aa473-3905-4a80-b561-0d28506553ee.gif" width="700">

### 🌟 Made with ❤️ for the Quantitative Trading & Algorithmic Finance Community 🌟

**If this project helped you, consider giving it a ⭐ star!**

<img src="https://user-images.githubusercontent.com/74038190/212284158-e840e285-664b-44d7-b79b-e264b5e54825.gif" width="300">

</div>
