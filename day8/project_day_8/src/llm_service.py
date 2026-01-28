import json
import random
import time
import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

class LLMServiceError(Exception):
    """Custom exception for LLM service errors."""
    pass

def call_llm(prompt: str, malform_chance: float = 0.5, use_real_llm: bool = False) -> str:
    """
    Simulates or makes a real LLM call.
    malform_chance: Probability (0.0-1.0) of returning malformed JSON if use_real_llm is False.
    use_real_llm: If True, attempts to use a real LLM (e.g., OpenAI via litellm).
    """
    if use_real_llm:
        print(f"[LLM Service] Calling real LLM (model: gpt-3.5-turbo)...")
        try:
            if not os.getenv("OPENAI_API_KEY"):
                raise LLMServiceError("OPENAI_API_KEY not set for real LLM calls.")

            response = completion(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0
            )
            content = response.choices[0].message.content
            print(f"[LLM Service] Real LLM response received.")
            return content
        except Exception as e:
            print(f"[LLM Service] Error calling real LLM: {e}")
            raise LLMServiceError(f"Real LLM call failed: {e}")
    else:
        time.sleep(0.1)
        
        is_correction_prompt = "correct your response" in prompt.lower() or "malformed json" in prompt.lower()
        
        if random.random() < malform_chance and not is_correction_prompt:
            print("[LLM Service] Simulating malformed output (initial call)...")
            malformed_options = [
                '{"name": "Write report", "due_date": "2023-12-31", "priority": "high"',
                'Here is the data: {"name": "Review code", "due_date": "2024-01-15", "priority": "medium"}'
            ]
            return random.choice(malformed_options)
        elif is_correction_prompt and random.random() < malform_chance * 0.5:
             print("[LLM Service] Simulating malformed output (correction attempt)...")
             return '{"name": "Fix bug", "due_date": "2024-02-01", "priority": "high"'
        else:
            print("[LLM Service] Simulating good output.")
            return '{"name": "Prepare presentation", "due_date": "2024-01-20", "priority": "low"}'
