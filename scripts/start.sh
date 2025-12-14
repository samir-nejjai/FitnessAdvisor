#!/bin/bash

# Agentic Execution Coach - Start Script

echo "🎯 Starting Agentic Execution Coach..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment (check both .venv and venv)
echo "📦 Activating virtual environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    source venv/bin/activate
fi

# Check if dependencies are installed
if ! python -c "import crewai" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please copy .env.example to .env and configure it."
    echo "   cp .env.example .env"
    exit 1
fi

echo ""
echo "🚀 Starting server..."
echo "   Web UI: http://localhost:8000/static/index.html"
echo "   API Docs: http://localhost:8000/docs"
echo ""

# Start the server
python run.py
