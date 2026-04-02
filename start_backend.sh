#!/bin/bash

echo "=========================================="
echo "API Evolution Manager - Backend Startup"
echo "=========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "Creating virtual environment..."
    cd backend
    python3 -m venv venv
    cd ..
fi

# Activate virtual environment
echo "Activating virtual environment..."
source backend/venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
cd backend
pip install -q -r requirements.txt

# Check for .env file
if [ ! -f "../.env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create a .env file with your OPENAI_API_KEY"
    echo "You can copy .env.example and fill in your API key:"
    echo "  cp .env.example .env"
    echo ""
    exit 1
fi

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "Starting FastAPI server on http://localhost:8000"
echo "API docs available at http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
