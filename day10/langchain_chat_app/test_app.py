import subprocess
import time
import os
import sys

# Assume the app.py is in the current directory
APP_PATH="./app.py"

def run_test():
    print("🧪 Running functional test for LangChain Chatbot...")

    # Set a dummy API key for testing purposes (it won't actually call OpenAI)
    # The app should still start up and try to initialize ChatOpenAI
    os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key-for-test" 

    # Start the app in a subprocess
    process = subprocess.Popen([sys.executable, APP_PATH],
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               text=True,
                               bufsize=1) # Line-buffered output

    # Give the app some time to start up
    time.sleep(3) 

    # Interact with the chatbot
    interactions = [
        ("Hello", "Hi there!"),
        ("My name is Alice", "Nice to meet you, Alice."),
        ("What is my name?", "Your name is Alice.")
    ]

    output_lines = []
    
    try:
        # Read initial welcome message
        for _ in range(5): # Read a few lines to get past initial prints
            line = process.stdout.readline()
            if line:
                output_lines.append(line.strip())
            else:
                break
        
        print("n--- Chatbot Test Log ---")
        for user_input, expected_response_part in interactions:
            print(f"Sending: {user_input}")
            process.stdin.write(user_input + '\n')
            process.stdin.flush()
            time.sleep(2) # Give LLM time to respond (even if mocked/failed)

            response_found = False
            for _ in range(5): # Read a few lines for the response
                line = process.stdout.readline()
                if line:
                    output_lines.append(line.strip())
                    print(f"Received: {line.strip()}")
                    if "Bot:" in line and expected_response_part.lower() in line.lower():
                        response_found = True
                        break
                else:
                    break
            
            if not response_found:
                print(f"🚨 Test Failed: Expected '{expected_response_part}' not found for input '{user_input}'.")
                print("Captured Output:")
                for l in output_lines:
                    print(l)
                return False
        
        print("✅ Functional test passed for basic memory recall!")
        return True

    except Exception as e:
        print(f"An error occurred during testing: {e}")
        return False
    finally:
        # Terminate the chatbot process
        if process.poll() is None: # If process is still running
            process.stdin.write("exit\n")
            process.stdin.flush()
            process.terminate()
            process.wait(timeout=5)
        # Clean up dummy API key
        del os.environ["OPENAI_API_KEY"]

if __name__ == "__main__":
    if run_test():
        print("nAll tests completed successfully.")
    else:
        print("nSome tests failed.")
        sys.exit(1)
