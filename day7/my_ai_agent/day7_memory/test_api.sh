#!/bin/bash
# API test script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

SERVER_URL="http://127.0.0.1:5000"
SESSION_ID="test_session_$(date +%s)"

echo "=== Testing API Endpoints ==="
echo ""

# Test 1: Health check (chat endpoint)
echo "Test 1: Sending chat message..."
RESPONSE=$(curl -s -X POST "$SERVER_URL/chat" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"hello\", \"session_id\": \"$SESSION_ID\"}")
echo "Response: $RESPONSE"
if echo "$RESPONSE" | grep -q "response"; then
    echo "✓ Test 1 PASSED"
else
    echo "✗ Test 1 FAILED"
    exit 1
fi
echo ""

# Test 2: Memory test
echo "Test 2: Testing memory (sending multiple messages)..."
curl -s -X POST "$SERVER_URL/chat" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"my name is Alice\", \"session_id\": \"$SESSION_ID\"}" > /dev/null

RESPONSE=$(curl -s -X POST "$SERVER_URL/chat" \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"what did i just say\", \"session_id\": \"$SESSION_ID\"}")
echo "Response: $RESPONSE"
if echo "$RESPONSE" | grep -q "Alice"; then
    echo "✓ Test 2 PASSED (Memory working)"
else
    echo "✗ Test 2 FAILED (Memory not working)"
    exit 1
fi
echo ""

# Test 3: Reset endpoint
echo "Test 3: Testing reset endpoint..."
RESPONSE=$(curl -s -X POST "$SERVER_URL/reset" \
    -H "Content-Type: application/json" \
    -d "{\"session_id\": \"$SESSION_ID\"}")
echo "Response: $RESPONSE"
if echo "$RESPONSE" | grep -q "reset\|not found"; then
    echo "✓ Test 3 PASSED"
else
    echo "✗ Test 3 FAILED"
    exit 1
fi
echo ""

echo "=== All API tests passed! ==="
