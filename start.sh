#!/bin/bash
# Start script for WeWin services

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "============================================"
echo "Starting WeWin services..."
echo "============================================"

# Kill any existing processes on ports 8080 and 8003
echo "Checking for existing services..."
pkill -f "serve_spa.py" 2>/dev/null || true
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

# Give backend time to start
sleep 2

# Start frontend
echo "Starting frontend on port 8080..."
cd Page
nohup python3 serve_spa.py > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started with PID: $FRONTEND_PID"
cd ..

# Save PIDs
echo "$BACKEND_PID" > backend.pid
echo "$FRONTEND_PID" > frontend.pid

echo ""
echo "============================================"
echo "Services started successfully!"
echo "- Frontend: http://$(hostname -I | awk '{print $1}'):8080"
echo "- Backend:  http://$(hostname -I | awk '{print $1}'):8003"
echo ""
echo "Logs:"
echo "- Frontend: $PROJECT_DIR/frontend.log"
echo "- Backend:  $PROJECT_DIR/backend.log"
echo ""
echo "To stop services: ./stop.sh"
echo "============================================"
