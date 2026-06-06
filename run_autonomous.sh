#!/bin/bash

# ReqMind AI - Autonomous Mode Launcher
# This script starts the backend and autonomous frontend

echo "🤖 Starting ReqMind AI - Autonomous Mode"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start backend in background
echo "🚀 Starting backend API on port 8000..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start autonomous frontend
echo "🤖 Starting autonomous frontend on port 3001..."
streamlit run frontend/app_autonomous.py --server.port 3001 --server.headless true

# Cleanup on exit
trap "kill $BACKEND_PID" EXIT
