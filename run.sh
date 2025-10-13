#!/bin/bash

echo "🎯 Starting Job Hunter Application..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running!"
    echo "Please start Ollama in another terminal:"
    echo "  ollama serve"
    echo ""
    echo "Then pull a model:"
    echo "  ollama pull llama3"
    echo ""
    read -p "Press Enter to continue anyway, or Ctrl+C to exit..."
fi

# Start the application
python -m app.web

