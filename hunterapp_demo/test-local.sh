#!/bin/bash
# Simple local server for testing the demo version
# Usage: ./test-local.sh [port]

PORT=${1:-8077}
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🚀 Starting local server for Hunter Demo..."
echo "📁 Serving from: $DIR"
echo "🌐 Open in browser: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$DIR"

# Try Python 3 first (most common)
if command -v python3 &> /dev/null; then
    python3 -m http.server $PORT
# Fallback to Python 2
elif command -v python &> /dev/null; then
    python -m SimpleHTTPServer $PORT
else
    echo "❌ Error: Python not found. Please install Python to run the local server."
    echo ""
    echo "Alternative options:"
    echo "  - Install Node.js and run: npx http-server -p $PORT"
    echo "  - Use any static file server of your choice"
    exit 1
fi
