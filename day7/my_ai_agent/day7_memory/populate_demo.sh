#!/bin/bash
# Script to populate dashboard with demo data
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SERVER_URL="http://127.0.0.1:5000"

# Check if server is running
if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Error: Flask server is not running on port 5000."
    echo "Please start the server first using: ./start_server.sh"
    exit 1
fi

echo "=== Populating Dashboard with Demo Data ==="
echo ""

# Create multiple sessions with conversations
echo "Creating demo conversations..."

# Session 1: Greeting conversation
SESSION1="demo_user_1"
curl -s -X POST "$SERVER_URL/chat" -H "Content-Type: application/json" \
    -d "{\"message\": \"hello\", \"session_id\": \"$SESSION1\"}" > /dev/null
curl -s -X POST "$SERVER_URL/chat" -H "Content-Type: application/json" \
    -d "{\"message\": \"my name is Alice\", \"session_id\": \"$SESSION1\"}" > /dev/null
curl -s -X POST "$SERVER_URL/chat" -H "Content-Type: application/json" \
    -d "{\"message\": \"what did i just say\", \"session_id\": \"$SESSION1\"}" > /dev/null

# Session 2: Another user
SESSION2="demo_user_2"
curl -s -X POST "$SERVER_URL/chat" -H "Content-Type: application/json" \
    -d "{\"message\": \"hello\", \"session_id\": \"$SESSION2\"}" > /dev/null
curl -s -X POST "$SERVER_URL/chat" -H "Content-Type: application/json" \
    -d "{\"message\": \"my name is Bob\", \"session_id\": \"$SESSION2\"}" > /dev/null

# Session 3: More activity
SESSION3="demo_user_3"
for i in {1..4}; do
    curl -s -X POST "$SERVER_URL/chat" -H "Content-Type: application/json" \
        -d "{\"message\": \"Message $i\", \"session_id\": \"$SESSION3\"}" > /dev/null
done

# Session 4 & 5: Additional sessions
SESSION4="demo_user_4"
SESSION5="demo_user_5"
for session in $SESSION4 $SESSION5; do
    curl -s -X POST "$SERVER_URL/chat" -H "Content-Type: application/json" \
        -d "{\"message\": \"Hello from $session\", \"session_id\": \"$session\"}" > /dev/null
    curl -s -X POST "$SERVER_URL/chat" -H "Content-Type: application/json" \
        -d "{\"message\": \"How are you?\", \"session_id\": \"$session\"}" > /dev/null
done

echo "Demo data generated!"
echo ""

# Show current metrics
METRICS=$(curl -s "$SERVER_URL/metrics")
ACTIVE_SESSIONS=$(echo "$METRICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('active_sessions', 0))" 2>/dev/null || echo "0")
TOTAL_MESSAGES=$(echo "$METRICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_messages', 0))" 2>/dev/null || echo "0")

echo "Current Dashboard Metrics:"
echo "  Active Sessions: $ACTIVE_SESSIONS"
echo "  Total Messages: $TOTAL_MESSAGES"
echo ""
echo "✓ Dashboard should now show non-zero values!"
echo "  Visit: http://127.0.0.1:5000/dashboard"
echo ""
