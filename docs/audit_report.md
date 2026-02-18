# Code Duplication Audit: `app.py` vs `server.py`

This document details the critical inconsistencies and duplication found between the CLI logic (`app.py`) and the Web Server logic (`server.py`).

## 1. Core Logic Duplication
Both files implement the entire download pipeline independently:
- **`app.py`**: Contains `run_download`, `_download_symbol`, and `_download_symbol_native`.
- **`server.py`**: Contains `run_download_job`, which is a copy-paste of the logic in `app.py` but modified to include WebSocket logging.

## 2. Inconsistencies

### Threading Model
- **CLI (`app.py`)**: Uses `concurrent.futures.ThreadPoolExecutor` with a `threading.Lock` to protect the `CSVDumper`. It creates a new executor *per symbol*.
- **Server (`server.py`)**: Also uses `ThreadPoolExecutor` but inside a function called `run_download_job`. It mixes async/await (for WebSocket broadcasting) with blocking thread operations.

### Progress Tracking
- **CLI**: Uses `utils.progress.DownloadProgress` (tqdm-based) for terminal output.
- **Server**: Manages a global `state` object (`JobState`) and broadcasts JSON updates via WebSockets. It calculates percentage manually based on `global_completed`.

### Error Handling
- **CLI**: Prints errors to stderr and continues or exits based on severity. Catches generic `Exception`.
- **Server**: Catches exceptions, updates the job status to `failed`, and logs to the internal memory log buffer.

### Configuration
- **CLI**: Hardcoded `0.5s` delay between thread submissions.
- **Server**: Hardcoded `0.3s` delay between thread submissions.
- **Retry Logic**: Both rely on `core/fetch.py`, but the invocation parameters (like `threads`) are passed differently.

### Native Candle Handling
- **CLI**: Checks `_should_use_native`.
- **Server**: Checks `use_native` inside `run_download_job` with slightly different logic (checking `data_source` string case sensitivity manually).

## 3. Maintenance Risk
- Any bug fix applied to `app.py` (e.g., the Midnight Bug fix) must be manually ported to `server.py`, or it will be missed.
- The `CSVDumper` instantiation is duplicated, meaning changes to the dumper's API require updating both files.

## 4. Unification Plan (Phase 5)
We will create a `DownloaderService` class in `core/service.py` that:
1.  Accepts a `DownloadConfig` object.
2.  Accepts a `ProgressObserver` interface (to decouple TQDM vs WebSocket).
3.  Accepts a `Logger` interface.
4.  Contains the single source of truth for the download loop (Symbol -> Days -> Fetch -> Aggregate -> Dump).

This will allow `cli.py` and `server.py` to become thin wrappers around `DownloaderService`.
