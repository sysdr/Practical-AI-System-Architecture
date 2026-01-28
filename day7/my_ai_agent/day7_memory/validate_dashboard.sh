#!/bin/bash
# Dashboard validation script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SERVER_URL="http://127.0.0.1:5000"

echo "=== Validating Dashboard Metrics ==="
echo ""

# Check if server is running
if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Error: Flask server is not running on port 5000."
    exit 1
fi

# Generate some activity to update metrics
echo "Generating test activity to populate metrics..."

# Create multiple sessions with messages
for session_num in {1..5}; do
    SESSION_ID="dashboard_test_$(date +%s)_$session_num"
    # Send 2-3 messages per session
    for msg_num in {1..3}; do
        curl -s -X POST "$SERVER_URL/chat" \
            -H "Content-Type: application/json" \
            -d "{\"message\": \"Test message $msg_num from session $session_num\", \"session_id\": \"$SESSION_ID\"}" > /dev/null
    done
done

echo "Test activity generated."
echo ""

# Check metrics and verify they are non-zero
echo "Checking metrics..."
METRICS=$(curl -s "$SERVER_URL/metrics")
ACTIVE_SESSIONS=$(echo "$METRICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('active_sessions', 0))" 2>/dev/null || echo "0")
TOTAL_MESSAGES=$(echo "$METRICS" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('total_messages', 0))" 2>/dev/null || echo "0")

echo "Current metrics:"
echo "  Active sessions: $ACTIVE_SESSIONS"
echo "  Total messages: $TOTAL_MESSAGES"
echo ""

if [ "$ACTIVE_SESSIONS" -gt 0 ] && [ "$TOTAL_MESSAGES" -gt 0 ]; then
    echo "✓ Metrics are non-zero and updating correctly"
    echo "✓ Dashboard should display: $ACTIVE_SESSIONS active sessions, $TOTAL_MESSAGES total messages"
else
    echo "⚠ Warning: Metrics are still zero. Dashboard may show zero values."
    echo "  Try refreshing the dashboard or sending more chat requests."
fi

echo ""
echo "=== Dashboard validation complete ==="
