#!/bin/bash

# Quick Start Script for Dealership Contact Automation
# Starts both backend and frontend servers

set -e

echo "=========================================="
echo " Dealership Contact Automation"
echo " Quick Start Script"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "WEBSOCKET_INTEGRATION_GUIDE.md" ]; then
    echo "❌ Error: Please run this script from the Auto Contacting directory"
    exit 1
fi

# Create screenshots directory if it doesn't exist
mkdir -p screenshots
echo "✓ Screenshots directory ready"

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo "⚠️  No virtual environment found"
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "✓ Activating virtual environment"
source venv/bin/activate

# Install/update backend dependencies
echo ""
echo "Checking backend dependencies..."
cd backend
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: backend/requirements.txt not found"
    exit 1
fi

pip install -q -r requirements.txt
echo "✓ Backend dependencies installed"

# Check main project dependencies
cd ..
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo "✓ Main project dependencies installed"
fi

echo ""
echo "=========================================="
echo " Starting Servers"
echo "=========================================="
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✓ Servers stopped"
    exit 0
}

trap cleanup EXIT INT TERM

# Start backend server
echo "Starting WebSocket backend server..."
cd backend
python websocket_server.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 2

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✓ Backend running on http://localhost:8001 (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start. Check logs/backend.log"
    exit 1
fi

# Start frontend server
echo "Starting frontend HTTP server..."
mkdir -p logs
cd frontend
python3 -m http.server 8000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 1

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "✓ Frontend running on http://localhost:8000 (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend failed to start. Check logs/frontend.log"
    exit 1
fi

echo ""
echo "=========================================="
echo " ✓ All Systems Ready!"
echo "=========================================="
echo ""
echo "Backend:   http://localhost:8001"
echo "Frontend:  http://localhost:8000"
echo "Logs:      logs/backend.log, logs/frontend.log"
echo ""
echo "🚀 Open http://localhost:8000 in your browser"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for user interrupt
wait
