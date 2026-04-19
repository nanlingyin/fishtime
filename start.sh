#!/usr/bin/env bash
# PlainList plugin entry point.
# Installs dependencies and starts fishtime backend + frontend.
# Killing this process also kills all child processes.

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
  kill 0
  exit
}
trap cleanup SIGTERM SIGINT

echo "[fishtime] Setting up Python venv and installing backend dependencies..."
cd "$DIR/backend"
PYTHON=$(command -v python3 || command -v python)
if [ ! -d "$DIR/.venv" ]; then
  $PYTHON -m venv "$DIR/.venv"
fi
source "$DIR/.venv/bin/activate"
pip install -r requirements.txt -q

echo "[fishtime] Starting backend on port 8000..."
cd "$DIR"
uvicorn backend.main:app --port 8000 &

echo "[fishtime] Installing frontend dependencies..."
cd "$DIR/frontend"
npm install --silent

echo "[fishtime] Starting frontend on port 5174..."
npm run dev -- --port 5174 &

echo "[fishtime] Ready."
wait
