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

from config.settings import TIMEFRAME_CHOICES, SYMBOLS, DEFAULT_THREADS, MAX_THREADS
from app import run_download, generate_days, count_days

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

# =============================================================================
# Request/Response Models
# =============================================================================
class DownloadRequest(BaseModel):
    symbols: List[str]
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    timeframe: str = "M1"
    threads: int = DEFAULT_THREADS

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
    """Run download in a background thread with log capture."""
    import concurrent.futures
    from core.fetch import fetch_day
    from core.processor import decompress
    from core.csv_dumper import CSVDumper
    from core.validator import validate_output
    from config.settings import TimeFrame, SATURDAY

    try:
        symbols = params["symbols"]
        start = datetime.strptime(params["start_date"], "%Y-%m-%d").date()
        end = datetime.strptime(params["end_date"], "%Y-%m-%d").date()
        timeframe_str = params["timeframe"]
        threads = min(params.get("threads", DEFAULT_THREADS), MAX_THREADS)

        tf_value = getattr(TimeFrame, timeframe_str.upper(), TimeFrame.TICK)
        all_days = list(generate_days(start, end))
        total_days = len(all_days)

        state.update_job(job_id, status="running", total_days=total_days * len(symbols))
        state.add_log(job_id, f"Starting download: {', '.join(symbols)}")
        state.add_log(job_id, f"Date range: {start} to {end} | Timeframe: {timeframe_str}")
        state.add_log(job_id, f"Trading days: {total_days} | Threads: {threads}")

        if total_days == 0:
            state.update_job(job_id, status="completed", progress=100)
            state.add_log(job_id, "No trading days in range.")
            return

        output_files = []
        global_completed = [0]
        global_total = total_days * len(symbols)

        for symbol in symbols:
            # Check for cancellation before starting symbol
            if state.cancel_events[job_id].is_set():
                break

            state.add_log(job_id, f"─── Downloading {symbol} ───")
            lock = threading.Lock()
            csv_dumper = CSVDumper(symbol, tf_value, start, end, DATA_DIR, header=True)

            def do_work(day, sym=symbol):
                try:
                    raw = fetch_day(sym, day)
                    ticks = decompress(sym, day, raw)
                    with lock:
                        csv_dumper.append(day, ticks)
                    tick_count = len(ticks) if ticks else 0
                    state.add_log(job_id, f"  ✓ {sym} {day} — {tick_count:,} ticks")
                except Exception as e:
                    state.add_log(job_id, f"  ✗ {sym} {day} — {str(e)[:80]}")
                finally:
                    global_completed[0] += 1
                    pct = round(global_completed[0] / global_total * 100, 1)
                    state.update_job(
                        job_id,
                        completed_days=global_completed[0],
                        progress=pct,
                    )
                    # Broadcast progress via event loop
                    try:
                        asyncio.run_coroutine_threadsafe(
                            state.broadcast_progress(job_id), state._loop
                        )
                    except Exception:
                        pass

            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures = []
                for i, day in enumerate(all_days):
                    # Check cancellation during submission
                    if state.cancel_events[job_id].is_set():
                        state.add_log(job_id, "⚠ Cancelling... stopping new tasks.")
                        break

                    futures.append(executor.submit(do_work, day))
                    if i > 0 and i % threads == 0:
                        time.sleep(0.3)
                concurrent.futures.wait(futures)

            if state.cancel_events[job_id].is_set():
                 state.add_log(job_id, "⚠ Symbol download cancelled.")
                 # Don't dump CSV if cancelled to avoid partial data?
                 # Or dump what we have? Let's dump what we have but mark as partial.
                 # Actually, usually users want to stop because they made a mistake.
                 # Let's write what we have but stop processing.
                 pass

            # Write CSV
            file_path = csv_dumper.dump()
            output_files.append(os.path.basename(file_path))
            state.add_log(job_id, f"  ✓ Written: {os.path.basename(file_path)}")

            # Validate
            results = validate_output(file_path, start, end, symbol)
            state.add_log(job_id, f"  Validation: {'VALID' if results['valid'] else 'ISSUES'} | {results['total_rows']:,} rows")

        if state.cancel_events[job_id].is_set():
            state.update_job(
                job_id,
                status="cancelled",
                finished_at=datetime.now().isoformat(),
                output_file=", ".join(output_files) if output_files else "Partial/None",
            )
            state.add_log(job_id, f"═══ Download Cancelled ═══")
        else:
            state.update_job(
                job_id,
                status="completed",
                progress=100,
                finished_at=datetime.now().isoformat(),
                output_file=", ".join(output_files),
            )
            state.add_log(job_id, f"═══ Download Complete ═══")

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
    webbrowser.open(f"http://localhost:{PORT}")

    uvicorn.run(
        "server:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="warning",
    )

