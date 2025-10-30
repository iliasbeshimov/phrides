#!/bin/bash

# Double-click launcher for macOS
# This file can be double-clicked from Finder to start everything

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "Stopped."
    sleep 2
}

trap cleanup EXIT INT TERM

# Clear screen
clear

echo "=================================================="
echo "  🚗 Dealership Contact Automation"
echo "=================================================="
echo ""

# Create necessary directories
mkdir -p logs screenshots backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up for first time..."
    python3 -m venv venv
    source venv/bin/activate

    # Install backend dependencies
    if [ -f "backend/requirements.txt" ]; then
        pip install -q -r backend/requirements.txt
    fi

    # Install main dependencies
    if [ -f "requirements.txt" ]; then
        pip install -q -r requirements.txt
    fi

    echo "✓ Setup complete!"
    echo ""
fi

# Activate virtual environment
source venv/bin/activate

echo "Starting backend server..."
cd backend
python websocket_server.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 3

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start"
    echo "Check logs/backend.log for errors"
    sleep 5
    exit 1
fi

echo "✓ Backend running (PID: $BACKEND_PID)"

echo "Starting frontend server..."
cd frontend
python3 -m http.server 8000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 2

if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Frontend failed to start"
    echo "Check logs/frontend.log for errors"
    sleep 5
    exit 1
fi

echo "✓ Frontend running (PID: $FRONTEND_PID)"
echo ""
echo "=================================================="
echo "  ✅ Everything is ready!"
echo "=================================================="
echo ""
echo "  Opening browser in 3 seconds..."
echo ""
echo "  URL: http://localhost:8000"
echo ""
echo "  Press Ctrl+C in this window to stop servers"
echo ""

# Wait a moment then open browser
sleep 3

# Open in default browser (macOS)
open http://localhost:8000

echo "✓ Browser opened"
echo ""
echo "Servers are running. Keep this window open."
echo "Press Ctrl+C to stop."
echo ""

# Keep script running
wait
