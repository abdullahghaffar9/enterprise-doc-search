#!/usr/bin/env python3
"""
One-click launcher: Backend + Frontend.
Press Ctrl+C to kill both processes.
"""
from __future__ import annotations


import os
import signal
import subprocess
import sys
import time
import socket
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND_DIR = ROOT / "backend"
FRONTEND_DIR = ROOT / "frontend"

backend_proc: subprocess.Popen | None = None
frontend_proc: subprocess.Popen | None = None


def _kill_both() -> None:
    global backend_proc, frontend_proc
    for name, proc in [("Backend", backend_proc), ("Frontend", frontend_proc)]:
        if proc is not None and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
            print(f"Stopped {name}.")


def _handler(_sig: int, _frame: object) -> None:
    print("\nShutting down...")
    _kill_both()
    sys.exit(0)


def find_free_port(start_port: int) -> int:
    port = start_port
    while port < 65535:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    raise RuntimeError("No free port found.")

def main() -> None:
    global backend_proc, frontend_proc

    if not (BACKEND_DIR / "app").exists():
        print("ERROR: backend/app not found. Run from project root.")
        sys.exit(1)
    if not (FRONTEND_DIR / "node_modules" / "vite").exists():
        print("ERROR: frontend/node_modules/vite not found. Run npm install in frontend.")
        sys.exit(1)

    signal.signal(signal.SIGINT, _handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _handler)

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    # Find free ports for backend and frontend
    backend_port = find_free_port(8000)
    frontend_port = find_free_port(5173)

    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "app.main"],
        cwd=str(BACKEND_DIR),
        env={**env, "PORT": str(backend_port)},
    )
    frontend_proc = subprocess.Popen(
        ["node", os.path.join("node_modules", "vite", "bin", "vite.js"), f"--port", str(frontend_port)],
        cwd=str(FRONTEND_DIR),
        env=env,
    )
    print(f'🚀 SYSTEM LAUNCHED: Go to http://localhost:{frontend_port}')
    print('Press Ctrl+C to stop both servers.')
    while True:
        backend_ret = backend_proc.poll() if backend_proc else 0
        frontend_ret = frontend_proc.poll() if frontend_proc else 0
        if backend_ret is not None or frontend_ret is not None:
            print('\nOne of the processes exited. Shutting down...')
            break
        time.sleep(1)


if __name__ == "__main__":
    main()
