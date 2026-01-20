import os
import openai
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file. Please set it.")

# --- Customer Feedback Data ---
CUSTOMER_FEEDBACK_TEXT = """
The new XYZ-Pro vacuum cleaner worked perfectly for the first two weeks,
but then the brush attachment stopped spinning. It makes a strange grinding
noise now. I'm very disappointed with the durability. Also, the battery life
is not as advertised; it only lasts about 20 minutes on full power.
The mobile app for scheduling cleans is intuitive though, that's a plus.
"""

def call_llm(prompt, model="gpt-3.5-turbo", max_tokens=150, temperature=0.7):
    """
    Generic function to call the LLM API.
    Includes basic error handling and retry mechanism.
    """
    for attempt in range(3): # Retry up to 3 times
        try:
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except openai.APIError as e:
            print(f"API Error on attempt {attempt + 1}: {e}")
            if attempt < 2:
                print("Retrying in 2 seconds...")
                import time
                time.sleep(2)
            else:
                raise
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise
    return None

def zero_shot_summarize(feedback_text):
    """
    Demonstrates zero-shot prompting for summarization.
    """
    print("\\n--- Zero-Shot Summarization ---")
    prompt = f"Summarize the following customer feedback:\\n\\n{feedback_text}"
    summary = call_llm(prompt)
    print("Zero-shot Summary:")
    print(summary)
    return summary

def few_shot_structured_summarize(feedback_text):
    """
    Demonstrates few-shot prompting with structured output and persona.
    Includes the assignment's new requirements (priority, max length for issue).
    """
    print("\\n--- Few-Shot Structured Summarization (with persona, delimiters, JSON output) ---")
    prompt = f"""
You are an expert product analyst, highly skilled in identifying critical product issues from customer feedback.
Your task is to summarize the provided customer feedback into a structured JSON object.
Focus on extracting the core issue, the customer's sentiment, the affected product area, and assign a priority (High, Medium, Low) based on severity.
The 'issue' field should be concise, no more than 20 words. If no clear issue is found, mark it as "N/A".

Examples:
---
Feedback: "My new phone's battery dies really fast, even after a full charge. It's so frustrating!"
Output: {{"issue": "Rapid battery drain", "sentiment": "Negative", "product_area": "Hardware", "priority": "High"}}
---
Feedback: "The new app update is fantastic! Love the dark mode feature and how smooth it runs."
Output: {{"issue": "App performance/features", "sentiment": "Positive", "product_area": "Software", "priority": "Low"}}
---
Feedback: "The delivery was delayed by a week, and the packaging was damaged. Product seems okay though."
Output: {{"issue": "Shipping delay and damaged packaging", "sentiment": "Negative", "product_area": "Logistics", "priority": "Medium"}}
---

Customer Feedback to summarize:
{feedback_text}

Please provide the output in JSON format only.
"""
    result = call_llm(prompt, max_tokens=200, temperature=0.3)
    print("Few-shot Structured Summary:")
    print(result)
    try:
        # Try to parse JSON from the response
        json_start = result.find("{")
        json_end = result.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            json_str = result[json_start:json_end]
            parsed = json.loads(json_str)
            print("\\nParsed JSON:")
            print(json.dumps(parsed, indent=2))
            return parsed
    except json.JSONDecodeError:
        print("Warning: Could not parse JSON from response")
    return result

if __name__ == "__main__":
    print("=" * 60)
    print("LLM Prompt Engineering Demo")
    print("=" * 60)
    
    # Zero-shot summarization
    zero_shot_summarize(CUSTOMER_FEEDBACK_TEXT)
    
    print("\\n" + "=" * 60)
    
    # Few-shot structured summarization
    few_shot_structured_summarize(CUSTOMER_FEEDBACK_TEXT)
