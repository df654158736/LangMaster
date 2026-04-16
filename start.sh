#!/usr/bin/env bash
# Start both backend and frontend in parallel. Ctrl+C shuts both down.

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

# First-run setup if needed
if [ ! -d "backend/venv" ]; then
  echo "[setup] creating backend venv..."
  python3 -m venv backend/venv
  backend/venv/bin/pip install -q -r backend/requirements.txt
fi

if [ ! -d "frontend/node_modules" ]; then
  echo "[setup] installing frontend deps..."
  (cd frontend && npm install)
fi

cleanup() {
  echo ""
  echo "[stop] shutting down..."
  [ -n "$BACKEND_PID" ] && kill "$BACKEND_PID" 2>/dev/null || true
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
  exit 0
}
trap cleanup INT TERM

echo "[backend] starting on :$BACKEND_PORT"
(cd backend && ./venv/bin/uvicorn app.main:app --port "$BACKEND_PORT" --reload) &
BACKEND_PID=$!

echo "[frontend] starting on :$FRONTEND_PORT"
(cd frontend && npm run dev -- --port "$FRONTEND_PORT") &
FRONTEND_PID=$!

echo ""
echo "LangMaster running:"
echo "  Backend:  http://localhost:$BACKEND_PORT (docs: /docs)"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo ""
echo "Press Ctrl+C to stop."

wait
