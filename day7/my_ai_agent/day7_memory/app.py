from flask import Flask, request, jsonify
import os

app = Flask(__name__)
chat_histories = {} # Store history: {session_id: ["User: msg1", "AI: resp1", ...]}

# In a real production system, this would be a more sophisticated LLM integration.
# For this hands-on, we simulate to focus on memory management.
def simulate_llm_response(full_prompt: str, user_message: str = "") -> str:
    """A very basic simulated LLM for demonstration purposes."""
    # Check "what did i just say" first (check current message, not full history)
    if user_message and "what did i just say" in user_message.lower():
        # This demonstrates the LLM actually *seeing* the full prompt
        # Find the previous user message (skip the current "what did i just say" message)
        lines = full_prompt.split('\n')
        last_user_msg = ""
        # Start from second-to-last line to skip the current message
        for i in range(len(lines) - 2, -1, -1):
            if lines[i].startswith("User:"):
                last_user_msg = lines[i].replace("User: ", "").strip()
                break
        if last_user_msg:
            return f"You just said: '{last_user_msg}'"
        return "I don't see any previous message from you."
    if "hello" in full_prompt.lower():
        return "Hello there! How can I assist you today?"
    if "my name is" in full_prompt.lower():
        name = full_prompt.split("my name is")[-1].split(".")[0].strip()
        return f"Nice to meet you, {name}! How can I help?"
    if "summarize" in full_prompt.lower():
        return "I can try to summarize. What information is most important?"
    return f"Acknowledged: '{full_prompt.split('User: ')[-1]}'. How can I elaborate?"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')
    session_id = data.get('session_id', 'default_session')

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    if session_id not in chat_histories:
        chat_histories[session_id] = []

    current_history = chat_histories[session_id]

    # Core logic: Construct prompt with history.
    # We apply a sliding window to manage context size and simulate token limits.
    # Keep up to 5 user-AI turns, which means 10 messages (5 user, 5 AI).
    context_window_size = 10 
    recent_history = current_history[-context_window_size:]

    full_prompt_lines = recent_history + [f"User: {user_message}"]
    full_prompt = "\n".join(full_prompt_lines)

    # Call the simulated LLM
    llm_response = simulate_llm_response(full_prompt, user_message)

    # Update history with both the user's message and the AI's response
    chat_histories[session_id].append(f"User: {user_message}")
    chat_histories[session_id].append(f"AI: {llm_response}")

    # Re-apply sliding window after adding new messages to ensure it doesn't grow indefinitely
    chat_histories[session_id] = chat_histories[session_id][-context_window_size:]

    return jsonify({"response": llm_response, "session_id": session_id})

@app.route('/reset', methods=['POST'])
def reset_session():
    session_id = request.json.get('session_id')
    if session_id in chat_histories:
        del chat_histories[session_id]
        return jsonify({"message": f"Session {session_id} reset."})
    return jsonify({"message": f"Session {session_id} not found."}), 404


@app.route('/metrics', methods=['GET'])
def metrics():
    """JSON metrics for dashboard."""
    total_sessions = len(chat_histories)
    total_messages = sum(len(h) for h in chat_histories.values())
    return jsonify({
        "active_sessions": total_sessions,
        "total_messages": total_messages,
        "sessions": {sid: {"message_count": len(h)} for sid, h in chat_histories.items()},
    })


@app.route('/dashboard', methods=['GET'])
@app.route('/', methods=['GET'])
def dashboard():
    """Dashboard URL: shows session and message metrics."""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Day 7 – Conversation State Dashboard</title>
    <style>
        body { font-family: system-ui, sans-serif; max-width: 640px; margin: 2rem auto; padding: 0 1rem; }
        h1 { color: #333; }
        .metric { background: #f0f4f8; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; }
        .metric strong { display: block; font-size: 1.5rem; color: #1a365d; }
        .meta { color: #64748b; font-size: 0.9rem; }
        a { color: #2563eb; }
        .chat-form { background: #fff; border: 1px solid #e2e8f0; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; }
        .chat-form h2 { margin-top: 0; color: #1a365d; font-size: 1.2rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; color: #475569; font-weight: 500; }
        .form-group input { width: 100%; padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 1rem; box-sizing: border-box; }
        .form-group input:focus { outline: none; border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
        button { background: #2563eb; color: white; border: none; padding: 0.75rem 1.5rem; border-radius: 6px; font-size: 1rem; cursor: pointer; font-weight: 500; }
        button:hover { background: #1d4ed8; }
        button:disabled { background: #94a3b8; cursor: not-allowed; }
        .status { margin-top: 1rem; padding: 0.75rem; border-radius: 6px; font-size: 0.9rem; }
        .status.success { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
        .status.error { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
        .status.info { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
    </style>
</head>
<body>
    <h1>Day 7 – Conversation State Dashboard</h1>
    <p class="meta">Metrics auto-update every 7 seconds. Send chat requests below to see values change in real-time.</p>
    <div id="metrics"></div>
    
    <div class="chat-form">
        <h2>Send Chat Request</h2>
        <form id="chatForm">
            <div class="form-group">
                <label for="message">Message:</label>
                <input type="text" id="message" name="message" placeholder="Enter your message (e.g., 'hello', 'my name is Alice')" required>
            </div>
            <div class="form-group">
                <label for="sessionId">Session ID (optional):</label>
                <input type="text" id="sessionId" name="sessionId" placeholder="Leave empty for auto-generated session">
            </div>
            <button type="submit" id="submitBtn">Send Chat Request</button>
        </form>
        <div id="status"></div>
    </div>
    
    <script>
        let currentSessionId = null;
        
        function load() {
            fetch('/metrics').then(r => r.json()).then(data => {
                document.getElementById('metrics').innerHTML =
                    '<div class="metric"><strong>' + data.active_sessions + '</strong> Active sessions</div>' +
                    '<div class="metric"><strong>' + data.total_messages + '</strong> Total messages</div>';
            }).catch(() => {
                document.getElementById('metrics').innerHTML = '<div class="metric">Could not load metrics.</div>';
            });
        }
        
        function showStatus(message, type) {
            const statusDiv = document.getElementById('status');
            statusDiv.className = 'status ' + type;
            statusDiv.textContent = message;
            setTimeout(() => {
                statusDiv.textContent = '';
                statusDiv.className = 'status';
            }, 5000);
        }
        
        function generateSessionId() {
            return 'dashboard_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }
        
        document.getElementById('chatForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            const message = document.getElementById('message').value;
            const sessionIdInput = document.getElementById('sessionId').value;
            const sessionId = sessionIdInput || currentSessionId || generateSessionId();
            
            if (!sessionIdInput) {
                currentSessionId = sessionId;
            }
            
            const submitBtn = document.getElementById('submitBtn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: sessionId
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    showStatus('✓ Chat request sent successfully! Response: ' + data.response, 'success');
                    // Update metrics immediately
                    load();
                    // Clear message input
                    document.getElementById('message').value = '';
                } else {
                    const error = await response.json();
                    showStatus('✗ Error: ' + (error.error || 'Failed to send request'), 'error');
                }
            } catch (error) {
                showStatus('✗ Error: ' + error.message, 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Chat Request';
            }
        });
        
        // Load metrics on page load and set interval
        load();
        setInterval(load, 7000); // Update every 7 seconds (5-10 second range)
    </script>
</body>
</html>
'''


if __name__ == '__main__':
    # Use 0.0.0.0 to make it accessible from Docker container
    app.run(host='0.0.0.0', port=5000, debug=False)
