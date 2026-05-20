#!/bin/bash
# Stop script for WeWin frontend service

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "Stopping WeWin frontend service..."

# Stop frontend
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm -f frontend.pid
fi

# Kill any remaining processes
pkill -f "serve_spa.py" 2>/dev/null || true

echo "Frontend service stopped."
