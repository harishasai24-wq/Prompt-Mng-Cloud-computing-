#!/bin/bash
# Start frontend server and open browser automatically

cd "$(dirname "$0")"

echo "🐆 Starting Prompt_Manager Frontend..."
echo "📍 URL: http://localhost:5500"

# Open browser after a short delay (in background)
(sleep 1 && open "http://localhost:5500/index.html") &

# Start the HTTP server
python3 -m http.server 5500
