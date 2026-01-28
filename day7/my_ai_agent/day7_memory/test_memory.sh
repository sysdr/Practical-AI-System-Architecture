#!/bin/bash
# Memory management test script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SERVER_URL="http://127.0.0.1:5000"
SESSION_ID="memory_test_$(date +%s)"

echo "=== Testing Memory Management ==="
echo ""

# Send multiple messages to test context window
echo "Sending 6 messages to test sliding window (max 5 turns = 10 messages)..."
for i in {1..6}; do
    RESPONSE=$(curl -s -X POST "$SERVER_URL/chat" \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"Message $i\", \"session_id\": \"$SESSION_ID\"}")
    echo "Message $i sent"
done

echo ""
echo "Testing if older messages are still accessible..."
RESPONSE=$(curl -s -X POST "$SERVER_URL/chat" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"what did i just say\", \"session_id\": \"$SESSION_ID\"}")
echo "Response: $RESPONSE"

if echo "$RESPONSE" | grep -q "Message 6"; then
    echo "✓ Memory test PASSED (Recent messages accessible)"
else
    echo "✗ Memory test FAILED"
    exit 1
fi

echo ""
echo "=== Memory management test passed! ==="
