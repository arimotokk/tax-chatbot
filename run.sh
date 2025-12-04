#!/bin/bash

# Japanese Tax Q&A Bot - Run Script

echo "Starting Japanese Tax Q&A Bot..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    ./venv/bin/pip install -q -r requirements.txt
    echo "✓ Virtual environment created"
fi

# Check if database exists
if [ ! -d "chroma_db" ]; then
    echo ""
    echo "⚠️  Database not found. Please run setup first:"
    echo "   ./venv/bin/python setup_db.py"
    echo ""
    exit 1
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  ANTHROPIC_API_KEY not set. Please set it:"
    echo "   export ANTHROPIC_API_KEY='your_key_here'"
    echo ""
    exit 1
fi

# Run the app
echo ""
echo "🚀 Starting Flask server..."
echo "   Open your browser to: http://localhost:5000"
echo ""
./venv/bin/python app.py
