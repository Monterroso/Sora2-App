#!/bin/bash
# Sora 2 Video Generator - Quick Start Script

echo "================================"
echo "  Sora 2 Video Generator"
echo "================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for API key
if [ -z "$OPENAI_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo "✓ Found .env file"
    else
        echo ""
        echo "⚠️  No API key found!"
        echo ""
        echo "Please set your OpenAI API key:"
        echo "  export OPENAI_API_KEY='sk-your-key-here'"
        echo ""
        echo "Or create a .env file:"
        echo "  echo 'OPENAI_API_KEY=sk-your-key' > .env"
        echo ""
    fi
else
    echo "✓ API key found in environment"
fi

echo ""
echo "🚀 Starting server..."
echo "   Open http://localhost:5000 in your browser"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

python3 app.py


