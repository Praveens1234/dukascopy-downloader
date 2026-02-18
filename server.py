"""
Dukascopy Downloader - FastAPI Web Server
Provides REST API + WebSocket for live terminal logs.
Serves the frontend UI and manages download jobs.
"""

import asyncio
import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    TIMEFRAME_CHOICES, SYMBOLS, DEFAULT_THREADS, MAX_THREADS,
    DATA_SOURCE_CHOICES, PRICE_TYPE_CHOICES, VOLUME_TYPE_CHOICES,
)
from core.service import DownloaderService, DownloadConfig, ProgressObserver
from core.validator import validate_output

# =============================================================================
# App Setup
# =============================================================================
app = FastAPI(title="Dukascopy Downloader", version="1.0.0")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

os.makedirs(DATA_DIR, exist_ok=True)

# =============================================================================
# Job State Management
# =============================================================================
class JobState:
    def __init__(self):
        self.jobs: Dict[str, dict] = {}
        self.log_subscribers: List[WebSocket] = []
        self.cancel_events: Dict[str, threading.Event] = {}
        self.lock = threading.Lock()
        self._loop = None

    def create_job(self, job_id, params):
        self.jobs[job_id] = {
            "id": job_id,
            "status": "pending",
            "params": params,
            "progress": 0,
            "total_days": 0,
            "completed_days": 0,
            "logs": [],
            "started_at": datetime.now().isoformat(),
            "finished_at": None,
            "output_file": None,
            "error": None,
        }
        self.cancel_events[job_id] = threading.Event()

    def update_job(self, job_id, **kwargs):
        with self.lock:
            if job_id in self.jobs:
                self.jobs[job_id].update(kwargs)

    def cancel_job(self, job_id):
        if job_id in self.cancel_events:
            self.cancel_events[job_id].set()
            self.update_job(job_id, status="cancelling")
            self.add_log(job_id, "⚠ Cancellation requested...")
            return True
        return False

    def add_log(self, job_id, message):
        with self.lock:
            if job_id in self.jobs:
                entry = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
                self.jobs[job_id]["logs"].append(entry)
                # Keep only last 500 log lines
                if len(self.jobs[job_id]["logs"]) > 500:
                    self.jobs[job_id]["logs"] = self.jobs[job_id]["logs"][-500:]

        # Broadcast to WebSocket subscribers
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._broadcast_log(job_id, entry),
                self._loop
            )

    async def _broadcast_log(self, job_id, entry):
        dead = []
        for ws in self.log_subscribers:
            try:
                await ws.send_json({"type": "log", "job_id": job_id, "message": entry})
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.log_subscribers.remove(ws)

    async def broadcast_progress(self, job_id):
        job = self.jobs.get(job_id)
        if not job:
            return
        dead = []
        for ws in self.log_subscribers:
            try:
                await ws.send_json({
                    "type": "progress",
                    "job_id": job_id,
                    "status": job["status"],
                    "progress": job["progress"],
                    "completed_days": job["completed_days"],
                    "total_days": job["total_days"],
                })
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.log_subscribers.remove(ws)

state = JobState()

class ServerProgressObserver(ProgressObserver):
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.output_files = []
        self.global_completed = 0
        self.global_total = 0

    def on_start(self, symbol: str, total_days: int):
        # We might call on_start multiple times if multiple symbols.
        # But DownloaderService calls it per symbol.
        # We need to track global progress if we want to show overall %
        # For now, let's just log it.
        state.add_log(self.job_id, f"─── Downloading {symbol} ({total_days} steps) ───")

    def on_update(self, symbol: str, days_processed: int, total_days: int, success: bool):
        # This is tricky because we might have multiple symbols.
        # Ideally, DownloaderService would report global progress, or we track it here.
        # Simple hack: Just update progress based on the current symbol context?
        # Better: let's just trust the service calls.

        # If we knew the grand total of days across all symbols, we could do better.
        # But DownloaderService processes sequentially.
        # So we can accumulate progress?
        pass # We will handle progress updates inside the wrapper logic or improve Service later.

        # Actually, let's use the log for granular updates
        if success and days_processed % 10 == 0:
             state.add_log(self.job_id, f"  ✓ {symbol}: {days_processed}/{total_days}")

    def on_finish(self, symbol: str, output_path: str):
        self.output_files.append(os.path.basename(output_path))
        state.add_log(self.job_id, f"  ✓ Written: {os.path.basename(output_path)}")

        # Run validation
        # We need start/end dates. We can get them from the job params.
        job = state.jobs.get(self.job_id)
        if job:
            s = job["params"]["start_date"]
            e = job["params"]["end_date"]
            try:
                # Validation requires datetime objects? No, wait.
                # validate_output expects datetime objects or strings?
                # core/validator.py: validate_output(file_path, start_date, end_date, symbol)
                # It uses them for internal logic. Let's pass what we have.
                # Ideally pass date objects.
                sd = datetime.strptime(s, "%Y-%m-%d").date()
                ed = datetime.strptime(e, "%Y-%m-%d").date()
                results = validate_output(output_path, sd, ed, symbol)
                state.add_log(self.job_id, f"  Validation: {'VALID' if results['valid'] else 'ISSUES'} | {results['total_rows']:,} rows")
            except Exception as e:
                state.add_log(self.job_id, f"  Validation Error: {e}")


    def on_error(self, symbol: str, error: Exception):
        state.add_log(self.job_id, f"  ✗ {symbol} Error: {str(error)}")

    def log(self, message: str):
        state.add_log(self.job_id, message)


# =============================================================================
# Request/Response Models
# =============================================================================
class DownloadRequest(BaseModel):
    symbols: List[str]
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    timeframe: str = "M1"
    threads: int = DEFAULT_THREADS
    data_source: str = "auto"   # auto, tick, native
    price_type: str = "BID"     # BID, ASK, MID
    volume_type: str = "TOTAL"  # TOTAL, BID, ASK, TICKS
    custom_tf: str = None       # Custom timeframe string e.g. '120', '5m'

class JobResponse(BaseModel):
    id: str
    status: str
    params: dict
    progress: float
    total_days: int
    completed_days: int
    started_at: str
    finished_at: Optional[str]
    output_file: Optional[str]
    error: Optional[str]

# =============================================================================
# Custom Download Runner (with log capture)
# =============================================================================
def run_download_job(job_id: str, params: dict):
    """Run download in a background thread using DownloaderService."""
    try:
        start_date = datetime.strptime(params["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(params["end_date"], "%Y-%m-%d").date()

        config = DownloadConfig(
            symbols=[s.upper() for s in params["symbols"]],
            start_date=start_date,
            end_date=end_date,
            timeframe=params["timeframe"],
            threads=min(params.get("threads", DEFAULT_THREADS), MAX_THREADS),
            data_source=params.get("data_source", "auto"),
            price_type=params.get("price_type", "BID"),
            volume_type=params.get("volume_type", "TOTAL"),
            custom_tf=params.get("custom_tf"),
            output_dir=DATA_DIR,
            header=True,
            resume=False
        )

        observer = ServerProgressObserver(job_id)
        service = DownloaderService(config, observer)

        # Inject cancel capability
        # The service checks cancel_event internally.
        # We need to bridge state.cancel_events[job_id] to service._cancel_event?
        # Or just polling.
        # Actually Service has a cancel() method.
        # But we are running service.run() which blocks.
        # So we need a way to trigger service.cancel() from outside.
        # We can poll state.cancel_events in the observer? No, observer is passive.

        # Solution: We can launch a monitor thread or just make the Observer check cancellation?
        # Or, we pass the cancel event to the config?
        # The Service creates its own event.
        # Let's override the Service's cancel event with ours?
        service._cancel_event = state.cancel_events[job_id]

        state.update_job(job_id, status="running")
        state.add_log(job_id, f"Starting download job...")

        service.run()

        if state.cancel_events[job_id].is_set():
             state.update_job(
                job_id,
                status="cancelled",
                finished_at=datetime.now().isoformat(),
                output_file="Partial"
            )
             state.add_log(job_id, "Download Cancelled.")
        else:
             # Check if any files produced
             output_files = observer.output_files
             state.update_job(
                job_id,
                status="completed",
                progress=100,
                finished_at=datetime.now().isoformat(),
                output_file=", ".join(output_files) if output_files else "None"
            )
             state.add_log(job_id, "Download Complete.")

    except Exception as e:
        state.update_job(job_id, status="failed", error=str(e),
                         finished_at=datetime.now().isoformat())
        state.add_log(job_id, f"FATAL ERROR: {str(e)}")


# =============================================================================
# API Routes
# =============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global handler to prevent server crashes from unhandled errors."""
    import traceback
    error_details = traceback.format_exc()
    print(f"🔥 UNHANDLED EXCEPTION: {exc}\n{error_details}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main frontend HTML."""
    html_path = os.path.join(STATIC_DIR, "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/config")
async def get_config():
    """Return available symbols, timeframes, and defaults."""
    return {
        "symbols": SYMBOLS,
        "timeframes": TIMEFRAME_CHOICES,
        "default_threads": DEFAULT_THREADS,
        "max_threads": MAX_THREADS,
        "volume_types": VOLUME_TYPE_CHOICES,
    }


@app.post("/api/download")
async def start_download(req: DownloadRequest):
    """Start a new download job."""
    job_id = str(uuid.uuid4())[:8]
    params = {
        "symbols": [s.upper() for s in req.symbols],
        "start_date": req.start_date,
        "end_date": req.end_date,
        "timeframe": req.timeframe,
        "threads": min(req.threads, MAX_THREADS),
        "data_source": req.data_source,
        "price_type": req.price_type,
        "volume_type": req.volume_type,
        "custom_tf": req.custom_tf,
    }
    state.create_job(job_id, params)

    # Run in background thread
    thread = threading.Thread(target=run_download_job, args=(job_id, params), daemon=True)
    thread.start()

    return {"job_id": job_id, "status": "started"}


@app.post("/api/jobs/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a running job."""
    if job_id not in state.jobs:
        return {"error": "Job not found"}, 404
    
    if state.jobs[job_id]["status"] in ["completed", "failed", "cancelled"]:
        return {"status": "already_finished"}

    success = state.cancel_job(job_id)
    return {"status": "cancelling" if success else "failed"}


@app.get("/api/jobs")
async def list_jobs():
    """List all jobs (recent first)."""
    jobs = sorted(state.jobs.values(), key=lambda j: j["started_at"], reverse=True)
    return [
        {k: v for k, v in j.items() if k != "logs"}
        for j in jobs
    ]


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get details of a specific job."""
    if job_id not in state.jobs:
        return {"error": "Job not found"}, 404
    return state.jobs[job_id]


@app.get("/api/files")
async def list_files():
    """List all CSV files in the data directory."""
    files = []
    if os.path.exists(DATA_DIR):
        for f in sorted(os.listdir(DATA_DIR), reverse=True):
            if f.endswith('.csv'):
                path = os.path.join(DATA_DIR, f)
                stat = os.stat(path)
                files.append({
                    "name": f,
                    "size": stat.st_size,
                    "size_human": _human_size(stat.st_size),
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })
    return files


@app.get("/api/files/{filename}")
async def download_file(filename: str):
    """Download a specific CSV file."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path) or not filename.endswith('.csv'):
        return {"error": "File not found"}, 404
    return FileResponse(path, filename=filename, media_type="text/csv")


@app.delete("/api/files/{filename}")
async def delete_file(filename: str):
    """Delete a specific CSV file."""
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path) and filename.endswith('.csv'):
        os.remove(path)
        return {"status": "deleted"}
    return {"error": "File not found"}, 404


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for live log streaming and progress updates."""
    await websocket.accept()
    state.log_subscribers.append(websocket)
    # Ensure loop is set if not already
    if state._loop is None:
        state._loop = asyncio.get_event_loop()

    try:
        while True:
            # Keep connection alive, handle client messages
            data = await websocket.receive_text()
            msg = json.loads(data)
            # Client can request full job log
            if msg.get("type") == "get_logs":
                job_id = msg.get("job_id")
                if job_id in state.jobs:
                    await websocket.send_json({
                        "type": "full_logs",
                        "job_id": job_id,
                        "logs": state.jobs[job_id]["logs"],
                    })
    except WebSocketDisconnect:
        if websocket in state.log_subscribers:
            state.log_subscribers.remove(websocket)


def _human_size(size_bytes):
    """Convert bytes to human readable string."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# =============================================================================
# Lifespan
# =============================================================================
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app):
    state._loop = asyncio.get_event_loop()
    yield

app.router.lifespan_context = lifespan


if __name__ == "__main__":
    import uvicorn
    import socket
    import webbrowser
    import signal

    PORT = 8000
    HOST = "0.0.0.0"  # Bind to ALL interfaces so mobile devices can connect

    # Get local network IP for mobile access
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    LOCAL_IP = get_local_ip()

    # Kill any existing process on the port (Windows)
    def kill_port(port):
        try:
            import subprocess
            result = subprocess.run(
                f'netstat -ano | findstr :{port}',
                shell=True, capture_output=True, text=True
            )
            for line in result.stdout.strip().split('\n'):
                if f':{port}' in line and 'LISTENING' in line:
                    pid = line.strip().split()[-1]
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True,
                                   capture_output=True)
                    print(f"  Killed existing process on port {port} (PID {pid})")
                    time.sleep(0.5)
        except Exception:
            pass

    # Check if port is in use
    def port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0

    if port_in_use(PORT):
        print(f"\n  ⚠ Port {PORT} is in use. Attempting to free it...")
        kill_port(PORT)
        time.sleep(1)
        if port_in_use(PORT):
            print(f"  ✗ Port {PORT} still in use. Trying port {PORT + 1}...")
            PORT += 1

    print(f"\n{'=' * 50}")
    print(f"  Dukascopy Downloader — Web UI")
    print(f"{'=' * 50}")
    print(f"  PC:     http://localhost:{PORT}")
    print(f"  Mobile: http://{LOCAL_IP}:{PORT}")
    print(f"{'=' * 50}")
    print(f"  Press Ctrl+C to stop\n")

    # Auto-open browser on PC
    # webbrowser.open(f"http://localhost:{PORT}")

    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="warning",
    )
