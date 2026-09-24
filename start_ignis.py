# start_ignis.py
"""
Local Production / Standalone Runner for IGNIS
Starts:
1. FastAPI Backend (port 8000)
2. Automation Worker (APScheduler running near real-time background jobs)
3. Frontend (production preview or dev server)
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
VENV_PYTHON = ROOT_DIR / "venv" / "Scripts" / "python.exe"
if not VENV_PYTHON.exists():
    VENV_PYTHON = Path(sys.executable)


def main():
    print("=" * 60)
    print("  IGNIS - Industrial Thermal Anomaly Monitoring Platform")
    print("  Starting all services in near real-time mode...")
    print("=" * 60)

    env = os.environ.copy()
    env["PROJECT_ROOT"] = str(ROOT_DIR)
    env["PYTHONPATH"] = f"{ROOT_DIR};{ROOT_DIR / 'backend'}"

    # 1. Start Backend API
    print("[1/3] Starting FastAPI Backend on http://127.0.0.1:8000...")
    backend_cmd = [
        str(VENV_PYTHON),
        "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--app-dir", "backend",
    ]
    backend_proc = subprocess.Popen(backend_cmd, cwd=str(ROOT_DIR), env=env)

    # 2. Start Automation Pipeline Worker
    print("[2/3] Starting Near Real-Time Automation Worker (every 30 mins)...")
    worker_cmd = [str(VENV_PYTHON), "automation/scheduler.py"]
    worker_proc = subprocess.Popen(worker_cmd, cwd=str(ROOT_DIR), env=env)

    # 3. Start Frontend (Vite preview or dev)
    print("[3/3] Starting Frontend...")
    # Check if npm can be invoked via cmd.exe
    frontend_cmd = ["cmd.exe", "/c", "npm --prefix frontend run preview -- --port 80 --host 0.0.0.0"]
    # Fallback to dev if preview not built
    if not (ROOT_DIR / "frontend" / "dist").exists():
        frontend_cmd = ["cmd.exe", "/c", "npm --prefix frontend run dev -- --host 0.0.0.0"]

    frontend_proc = subprocess.Popen(frontend_cmd, cwd=str(ROOT_DIR), env=env)

    print("\n" + "=" * 60)
    print("  IGNIS is RUNNING!")
    print("  - Backend API:    http://localhost:8000 (Docs: /docs)")
    print("  - Frontend UI:    http://localhost")
    print("  - Worker:         Active (background polling)")
    print("  Press Ctrl+C to terminate all services.")
    print("=" * 60 + "\n")

    try:
        while True:
            time.sleep(1)
            # Monitor process health
            if backend_proc.poll() is not None:
                print("WARNING: Backend process exited.")
                break
            if worker_proc.poll() is not None:
                print("WARNING: Worker process exited.")
                break
    except KeyboardInterrupt:
        print("\nShutting down IGNIS services gracefully...")
    finally:
        for proc in [backend_proc, worker_proc, frontend_proc]:
            try:
                proc.terminate()
                proc.wait(timeout=3)
            except Exception:
                proc.kill()
        print("All IGNIS services stopped.")


if __name__ == "__main__":
    main()
