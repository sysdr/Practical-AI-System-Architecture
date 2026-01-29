from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
import os
import json
from dotenv import load_dotenv
from datetime import datetime as dt

# Load environment variables from .env file
load_dotenv()

# --- Metrics (for dashboard) ---
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.join(PROJECT_DIR, "metrics.json")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:5000")

def load_metrics():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "total_messages_sent": 0,
        "total_messages_received": 0,
        "total_conversations": 0,
        "last_activity": None,
        "messages": []
    }

def save_metrics(metrics):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)
    try:
        import requests
        requests.get(f"{DASHBOARD_URL}/update", timeout=0.1)
    except Exception:
        pass

def update_metrics(user_msg, bot_msg):
    metrics = load_metrics()
    metrics["total_messages_sent"] += 1
    metrics["total_messages_received"] += 1
    metrics["last_activity"] = dt.now().isoformat()
    metrics["messages"].append({
        "timestamp": metrics["last_activity"],
        "user": user_msg[:80],
        "bot_preview": (bot_msg or "")[:80]
    })
    if len(metrics["messages"]) > 100:
        metrics["messages"] = metrics["messages"][-100:]
    save_metrics(metrics)

# --- Configuration ---
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("Error: OPENAI_API_KEY environment variable not set.")
    print("Please set it before running the application.")
    print("Example: export OPENAI_API_KEY='your_api_key_here'")
    exit(1)

MODEL_NAME = os.getenv("LLM_MODEL", "gpt-3.5-turbo")

# --- Initialize LLM and Memory ---
try:
    llm = ChatOpenAI(temperature=0.7, model=MODEL_NAME, api_key=openai_api_key)
    memory = ConversationBufferMemory()
    conversation = ConversationChain(llm=llm, memory=memory, verbose=True)
except Exception as e:
    print(f"Failed to initialize LLM or ConversationChain: {e}")
    exit(1)

# --- Chat Loop ---
def run_chat_app():
    metrics = load_metrics()
    metrics["total_conversations"] += 1
    save_metrics(metrics)

    print("\n--- Welcome to the LangChain Chatbot! ---")
    print(f"Using LLM: {MODEL_NAME}")
    print("Type 'exit' to quit the conversation.")
    print("------------------------------------------\n")

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Exiting chat. Goodbye!")
                break
            response = conversation.predict(input=user_input)
            print(f"Bot: {response}")
            update_metrics(user_input, response)
        except Exception as e:
            print(f"An error occurred during chat: {e}")
            continue

if __name__ == "__main__":
    run_chat_app()
