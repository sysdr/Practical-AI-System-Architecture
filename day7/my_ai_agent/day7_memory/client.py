import requests
import uuid
import os
import time

SERVER_URL = "http://127.0.0.1:5000/chat"
RESET_URL = "http://127.0.0.1:5000/reset"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    session_id = str(uuid.uuid4())
    clear_screen()
    print(f"--- Starting New Chat Session (ID: {session_id}) ---")
    print("Type 'exit' to end, 'reset' to clear conversation history.")
    print("--------------------------------------------------")

    while True:
        try:
            user_input = input(f"You ({session_id}): ").strip()
        except EOFError: # Handle Ctrl+D
            print("\nEnding chat session due to EOF. Goodbye!")
            break
        except KeyboardInterrupt: # Handle Ctrl+C
            print("\nEnding chat session. Goodbye!")
            break

        if user_input.lower() == 'exit':
            print("Ending chat session. Goodbye!")
            break
        elif user_input.lower() == 'reset':
            try:
                response = requests.post(RESET_URL, json={'session_id': session_id})
                response.raise_for_status()
                print(f"[System] {response.json().get('message')}")
            except requests.exceptions.ConnectionError:
                print("[Error] Could not connect to the server. Please ensure the Flask server is running.")
            except requests.exceptions.RequestException as e:
                print(f"[Error] Failed to reset session: {e}")
            continue

        try:
            response = requests.post(SERVER_URL, json={'message': user_input, 'session_id': session_id})
            response.raise_for_status()
            data = response.json()
            ai_response = data.get('response', 'No response from AI.')
            print(f"AI ({session_id}): {ai_response}")
        except requests.exceptions.ConnectionError:
            print("[Error] Could not connect to the server. Please ensure the Flask server is running.")
            break
        except requests.exceptions.RequestException as e:
            print(f"[Error] An error occurred: {e}")
            break

if __name__ == '__main__':
    main()
