#!/bin/bash

echo "=========================================="
echo "API Evolution Manager - Frontend Startup"
echo "=========================================="
echo ""

# Check if Python's http.server is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is required but not found"
    exit 1
fi

echo "Starting frontend server on http://localhost:5173"
echo ""
echo "Open your browser and navigate to:"
echo "  http://localhost:5173"
echo ""
echo "Make sure the backend is running on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start simple HTTP server
cd frontend
python3 -m http.server 5173
