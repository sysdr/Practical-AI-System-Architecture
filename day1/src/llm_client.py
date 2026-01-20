import os
import openai
from dotenv import load_dotenv
import sys

def get_llm_response(prompt_message: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7, max_tokens: int = 150):
    """
    Makes an API call to a foundational LLM (OpenAI Chat API) and returns its raw output.
    """
    # Load environment variables from .env file in the config directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')
    load_dotenv(dotenv_path)
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("\033[0;31mError: OPENAI_API_KEY not found in environment or config/.env file.\033[0m")
        print("\033[1;33mPlease set it before running the script (e.g., in config/.env).\033[0m")
        return None

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        print(f"\n--- Sending request to LLM (Model: {model}) ---")
        print(f"Prompt: '{prompt_message}'")
        print(f"Temperature: {temperature}, Max Tokens: {max_tokens}")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        print("\n--- Raw LLM Response ---")
        return response

    except openai.APIError as e:
        print(f"\033[0;31mOpenAI API Error: {e}\033[0m")
        return None
    except Exception as e:
        print(f"\033[0;31mAn unexpected error occurred: {e}\033[0m")
        return None

if __name__ == "__main__":
    print("\033[0;34m--- LLM Interaction Demo ---\033[0m")
    
    # Default prompt for demonstration
    default_prompt = "Explain the concept of 'distributed consensus' in a simple way."
    
    # Check for command line arguments for a custom prompt
    if len(sys.argv) > 1:
        custom_prompt_parts = sys.argv[1:]
        default_prompt = " ".join(custom_prompt_parts)

    llm_output = get_llm_response(default_prompt)

    if llm_output:
        print(llm_output.model_dump_json(indent=2)) # Pretty print the Pydantic model
        print("\n--- Extracted Content ---")
        print(llm_output.choices[0].message.content)
    else:
        print("\nFailed to get LLM response.")
