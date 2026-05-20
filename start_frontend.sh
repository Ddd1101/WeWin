#!/bin/bash
# Start script for WeWin frontend service

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "============================================"
echo "Starting WeWin frontend service..."
echo "============================================"

# Kill any existing frontend processes
echo "Checking for existing frontend service..."
pkill -f "serve_spa.py" 2>/dev/null || true
sleep 1

# Start frontend
echo "Starting frontend on port 8080..."
cd Page
nohup python3 serve_spa.py > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"
cd ..

# Save PID
echo "$FRONTEND_PID" > frontend.pid

echo ""
echo "============================================"
echo "Frontend service started successfully!"
echo "- Frontend: http://$(hostname -I | awk '{print $1}'):8080"
echo ""
echo "Logs: $PROJECT_DIR/frontend.log"
echo "To stop: ./stop_frontend.sh"
echo "============================================"
