#!/bin/bash
# Start script for WeWin frontend service (system nginx)

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

NGINX_BIN="/usr/sbin/nginx"
NGINX_CONF="$PROJECT_DIR/nginx_system.conf"
NGINX_PID="/tmp/nginx.pid"

echo "============================================"
echo "Starting WeWin frontend service..."
echo "============================================"

# Ensure log directory exists
mkdir -p "$PROJECT_DIR/nginx/logs"

# Stop any existing frontend processes
echo "Checking for existing frontend service..."
if [ -f "$NGINX_PID" ]; then
    OLD_PID=$(cat "$NGINX_PID")
    if kill -0 "$OLD_PID" 2>/dev/null; then
        echo "Stopping existing nginx (PID: $OLD_PID)..."
        "$NGINX_BIN" -s stop 2>/dev/null || kill "$OLD_PID" 2>/dev/null
        sleep 1
    fi
    rm -f "$NGINX_PID"
fi
# Also clean up any legacy serve_spa.py processes
pkill -f "serve_spa.py" 2>/dev/null || true

# Start nginx
echo "Starting nginx on port 8080..."
"$NGINX_BIN" -c "$NGINX_CONF"

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================"
    echo "Frontend service started successfully!"
    echo "- Frontend: http://$(hostname -I | awk '{print $1}'):8080"
    echo ""
    echo "Logs: $PROJECT_DIR/nginx/logs/"
    echo "To stop: ./stop_frontend.sh"
    echo "To reload: $NGINX_BIN -s reload"
    echo "============================================"
else
    echo "ERROR: Failed to start nginx"
    echo "Check logs: $PROJECT_DIR/nginx/logs/error.log"
    exit 1
fi
