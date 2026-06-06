#!/bin/bash

# ReqMind AI - SaaS Dashboard Launcher
# Professional Uizard-style interface

echo "🎯 ReqMind AI - SaaS Dashboard"
echo "================================"
echo ""

# Check if virtual environment exists
if [ ! -d "../venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source ../venv/bin/activate

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend not detected"
    echo "Please start backend in another terminal:"
    echo "  source venv/bin/activate"
    echo "  uvicorn app.main:app --reload"
    echo ""
fi

# Start SaaS dashboard
echo "🚀 Starting SaaS Dashboard..."
echo "📍 URL: http://localhost:8503"
echo ""
echo "Press Ctrl+C to stop"
echo ""

streamlit run app_saas.py --server.headless true --server.port 8503
