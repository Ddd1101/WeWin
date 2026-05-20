#!/bin/bash
# Start script for WeWin backend service

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "============================================"
echo "Starting WeWin backend service..."
echo "============================================"

# Kill any existing backend processes
echo "Checking for existing backend service..."
pkill -f "manage.py runserver" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 1

# Start backend
echo "Starting backend on port 8003..."
cd Server
source venv/bin/activate
nohup python3 manage.py runserver 0.0.0.0:8003 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"
cd ..

# Save PID
echo "$BACKEND_PID" > backend.pid

echo ""
echo "============================================"
echo "Backend service started successfully!"
echo "- Backend: http://$(hostname -I | awk '{print $1}'):8003"
echo ""
echo "Logs: $PROJECT_DIR/backend.log"
echo "To stop: ./stop_backend.sh"
echo "============================================"
