#!/usr/bin/env bash
set -e

# Start backend in background
uv run python run.py &
BACKEND_PID=$!

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT

# Poll health endpoint until backend is ready
echo "Waiting for backend..."
until curl -sf http://localhost:8000/docs > /dev/null 2>&1; do
  sleep 0.5
done
echo "Backend ready."

# Start frontend (blocks in foreground)
cd frontend && bun run dev