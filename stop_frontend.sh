#!/bin/bash
# Stop script for WeWin frontend service (system nginx)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

NGINX_BIN="/usr/sbin/nginx"
NGINX_PID="/tmp/nginx.pid"

echo "Stopping WeWin frontend service..."

# Try graceful stop via nginx command first
if [ -f "$NGINX_PID" ]; then
    "$NGINX_BIN" -s quit 2>/dev/null
    NGINX_PID_VAL=$(cat "$NGINX_PID")
    if kill -0 "$NGINX_PID_VAL" 2>/dev/null; then
        echo "Waiting for nginx to stop (PID: $NGINX_PID_VAL)..."
        for i in $(seq 1 20); do
            if ! kill -0 "$NGINX_PID_VAL" 2>/dev/null; then
                break
            fi
            sleep 0.5
        done
    fi
fi

# Force kill all nginx processes
NGINX_PIDS=$(pgrep -f "/usr/sbin/nginx" 2>/dev/null)
if [ -n "$NGINX_PIDS" ]; then
    echo "Force stopping nginx processes: $NGINX_PIDS"
    kill -9 $NGINX_PIDS 2>/dev/null
    sleep 1
fi

# Verify port is released
if ss -tlnp | grep -q ":8080 "; then
    echo "WARNING: Port 8080 still in use, killing process..."
    FUSER_PID=$(ss -tlnp | grep ":8080 " | grep -oP 'pid=\K[0-9]+' | head -1)
    [ -n "$FUSER_PID" ] && kill -9 "$FUSER_PID" 2>/dev/null
    sleep 1
fi

rm -f "$NGINX_PID"

# Also clean up any legacy serve_spa.py processes
pkill -f "serve_spa.py" 2>/dev/null || true
[ -f frontend.pid ] && rm -f frontend.pid

echo "Frontend service stopped."
