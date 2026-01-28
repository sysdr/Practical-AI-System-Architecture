#!/bin/bash
# Script to continuously send chat requests for real-time dashboard updates
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SERVER_URL="http://127.0.0.1:5000"

# Check if server is running
if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Error: Flask server is not running on port 5000."
    echo "Please start the server first using: ./start_server.sh"
    exit 1
fi

echo "=== Continuous Real-Time Updates ==="
echo "This script will send chat requests every 8 seconds"
echo "Watch your dashboard update in real-time!"
echo "Press Ctrl+C to stop"
echo ""

COUNTER=1
while true; do
    SESSION_ID="realtime_$(date +%s)_$COUNTER"
    MESSAGE="Real-time update #$COUNTER at $(date +%H:%M:%S)"
    
    curl -s -X POST "$SERVER_URL/chat" -H "Content-Type: application/json" \
        -d "{\"message\": \"$MESSAGE\", \"session_id\": \"$SESSION_ID\"}" > /dev/null
    
    METRICS=$(curl -s "$SERVER_URL/metrics")
    ACTIVE_SESSIONS=$(echo "$METRICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('active_sessions', 0))" 2>/dev/null || echo "0")
    TOTAL_MESSAGES=$(echo "$METRICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_messages', 0))" 2>/dev/null || echo "0")
    
    echo "[$COUNTER] Sent update - Sessions: $ACTIVE_SESSIONS, Messages: $TOTAL_MESSAGES"
    
    COUNTER=$((COUNTER + 1))
    sleep 8
done
