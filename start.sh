#!/usr/bin/env bash
# Start both backend and frontend in parallel. Ctrl+C shuts both down.

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

if ! command -v uv >/dev/null 2>&1; then
  echo "[error] uv is required to start the backend" >&2
  exit 1
fi

echo "[setup] syncing backend dependencies..."
(cd backend && uv sync --locked)

if [ ! -d "frontend/node_modules" ]; then
  echo "[setup] installing frontend deps..."
  (cd frontend && npm install)
fi

cleanup() {
  [ -n "${BACKEND_PID:-}" ] && kill "$BACKEND_PID" 2>/dev/null || true
  [ -n "${FRONTEND_PID:-}" ] && kill "$FRONTEND_PID" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

echo "[backend] starting on :$BACKEND_PORT"
(cd backend && uv run --no-sync uvicorn app.main:app --port "$BACKEND_PORT" --reload) &
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

wait -n "$BACKEND_PID" "$FRONTEND_PID"
echo "[error] a service stopped unexpectedly" >&2
exit 1
