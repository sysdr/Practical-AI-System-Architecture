import ollama
import sys
import os
import json
from datetime import datetime as dt

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.join(PROJECT_DIR, "metrics.json")

def load_metrics():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "total_questions_asked": 0,
        "total_responses": 0,
        "last_activity": None,
        "questions": []
    }

def save_metrics(metrics):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

def update_metrics(question, response):
    metrics = load_metrics()
    metrics["total_questions_asked"] = metrics.get("total_questions_asked", 0) + 1
    metrics["total_responses"] = metrics.get("total_responses", 0) + 1
    metrics["last_activity"] = dt.now().isoformat()
    metrics.setdefault("questions", []).append({
        "timestamp": metrics["last_activity"],
        "question_preview": (question or "")[:80],
        "response_preview": (response or "")[:80]
    })
    if len(metrics["questions"]) > 100:
        metrics["questions"] = metrics["questions"][-100:]
    save_metrics(metrics)

def demonstrate_hallucination():
    print("\n--- Demonstrating LLM Hallucination ---")
    question = "Who won the 2023 Nobel Prize in Physics for their work on quantum entanglement?"
    print(f"\nQuestion: {question}")
    print("Expecting the LLM to possibly hallucinate or give outdated info.\n")

    try:
        response = ollama.chat(
            model='llama2',
            messages=[{'role': 'user', 'content': question}],
            options={'temperature': 0.7}
        )
        llm_response = response['message']['content']
        print(f"LLM's Answer:\n{llm_response}")

        update_metrics(question, llm_response)
        print("\n--- Verification Hint ---")
        print("2023 Nobel Physics went to Anne L'Huillier, Pierre Agostini, Ferenc Krausz (attosecond physics).")
        print("Question mentioned 'quantum entanglement' (2022 topic) to see if the LLM corrects or hallucinates.")

    except Exception as e:
        print(f"Error: {e}")
        print("Ensure Ollama is running and 'llama2' is pulled.")
        sys.exit(1)

if __name__ == "__main__":
    demonstrate_hallucination()
