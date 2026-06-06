#!/bin/bash
# Startup script for ReqMind AI Frontend

echo "🎯 Starting ReqMind AI Frontend..."
echo ""
echo "Make sure the backend is running at http://127.0.0.1:8000"
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null
then
    echo "❌ Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run streamlit
streamlit run app.py
