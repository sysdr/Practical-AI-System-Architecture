# main.py
import os
import json
import time
import textwrap
from datetime import datetime
from openai import OpenAI, APIError, RateLimitError
import requests

# --- Configuration ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it to your OpenAI API key.")

client = OpenAI(api_key=OPENAI_API_KEY)
LLM_MODEL = "gpt-3.5-turbo"  # Or "gpt-4-turbo" for higher quality/cost
METRICS_FILE = "metrics.json"
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:5000")

# --- Metrics Functions ---
def load_metrics():
    """Load metrics from JSON file."""
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "total_requests": 0,
        "successful_processing": 0,
        "failed_processing": 0,
        "step1_summaries": 0,
        "step2_rewrites": 0,
        "step3_keywords": 0,
        "total_latency_ms": 0,
        "average_latency_ms": 0.0,
        "last_request_time": None,
        "requests": []
    }

def save_metrics(metrics):
    """Save metrics to JSON file."""
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)

def update_metrics(latency_ms, success=True, step1=False, step2=False, step3=False):
    """Update metrics with new request data."""
    metrics = load_metrics()
    metrics["total_requests"] += 1
    metrics["total_latency_ms"] += latency_ms
    metrics["average_latency_ms"] = metrics["total_latency_ms"] / metrics["total_requests"]
    metrics["last_request_time"] = datetime.now().isoformat()
    
    if success:
        metrics["successful_processing"] += 1
    else:
        metrics["failed_processing"] += 1
    
    if step1:
        metrics["step1_summaries"] += 1
    if step2:
        metrics["step2_rewrites"] += 1
    if step3:
        metrics["step3_keywords"] += 1
    
    # Keep last 100 requests
    metrics["requests"].append({
        "latency_ms": latency_ms,
        "success": success,
        "step1": step1,
        "step2": step2,
        "step3": step3,
        "timestamp": datetime.now().isoformat()
    })
    if len(metrics["requests"]) > 100:
        metrics["requests"] = metrics["requests"][-100:]
    
    save_metrics(metrics)
    
    # Update dashboard if available
    try:
        requests.get(f"{DASHBOARD_URL}/update", timeout=0.1)
    except:
        pass  # Dashboard might not be running

def call_llm(prompt_text: str, temperature: float = 0.7, retries: int = 2, delay: int = 5) -> str:
    """Helper function to call the LLM API with basic retry logic."""
    if not client.api_key:
        print("Error: OPENAI_API_KEY environment variable not set. Please set it before running.")
        return "LLM Error: API Key Missing"

    for attempt in range(retries + 1):
        try:
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt_text}
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            print(f"--- Attempt {attempt + 1}/{retries + 1}: Rate limit hit. Retrying in {delay} seconds...")
            time.sleep(delay)
        except APIError as e:
            print(f"--- Attempt {attempt + 1}/{retries + 1}: OpenAI API Error: {e}")
            if attempt < retries:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                return f"LLM API Error: {e}"
        except Exception as e:
            print(f"--- Attempt {attempt + 1}/{retries + 1}: General LLM Error: {e}")
            return f"LLM Error: {e}"
    return "LLM Error: Max retries exceeded."

def echo_section_header(title):
    print(f"\n===================================================")
    print(f"  {title}")
    print(f"===================================================")

def echo_section_content(content):
    # This function is for printing content from Python to stdout,
    # which will be captured by the main script for console dashboarding.
    # It wraps text for better readability in the console.
    print(textwrap.fill(content, width=80))

def summarize_article(article_content: str) -> str:
    """Step 1: Summarize the given article into concise bullet points."""
    echo_section_header("STEP 1: GENERATING SUMMARY")
    prompt = textwrap.dedent(f"""
    Summarize the following article into 3-4 concise bullet points.
    Focus on the main ideas and key takeaways.

    Article:
    ---
    {article_content}
    ---
    """)
    summary = call_llm(prompt, temperature=0.3)  # Lower temp for factual summary
    echo_section_content("Summary Generated:")
    echo_section_content(summary)
    return summary

def rewrite_summary(summary_content: str) -> str:
    """Step 2: Rewrite the summary into a casual, engaging paragraph."""
    echo_section_header("STEP 2: REWRITING SUMMARY")
    prompt = textwrap.dedent(f"""
    Take the following summary and rewrite it into a single, casual, and engaging paragraph.
    Imagine you are explaining it to a friend or for a blog post.
    Make it easy to understand and conversational.

    Summary to rewrite:
    ---
    {summary_content}
    ---
    """)
    rewritten_text = call_llm(prompt, temperature=0.7)  # Higher temp for more creativity
    echo_section_content("Rewritten Summary Generated:")
    echo_section_content(rewritten_text)
    return rewritten_text

def extract_keywords(text_to_analyze: str) -> str:
    """Step 3: Extract 5-7 key terms or phrases from the given text."""
    echo_section_header("STEP 3: EXTRACTING KEYWORDS")
    prompt = textwrap.dedent(f"""
    Extract 5-7 key terms or phrases from the following text, presented as a comma-separated list.
    Focus on the most important concepts.

    Text to analyze:
    ---
    {text_to_analyze}
    ---
    """)
    keywords = call_llm(prompt, temperature=0.2)  # Very low temp for deterministic extraction
    echo_section_content("Extracted Keywords:")
    echo_section_content(keywords)
    return keywords

def process_article(article_content: str):
    """Process an article through all three steps with metrics tracking."""
    overall_start_time = time.perf_counter()
    
    try:
        # Step 1: Summarize the article
        initial_summary = summarize_article(article_content)
        if "LLM Error" in initial_summary:
            echo_section_content("Summary step failed. Aborting.")
            overall_end_time = time.perf_counter()
            latency_ms = (overall_end_time - overall_start_time) * 1000
            update_metrics(latency_ms, success=False, step1=False, step2=False, step3=False)
            return None
        
        # Step 2: Rewrite the summary
        final_rewritten_text = rewrite_summary(initial_summary)
        if "LLM Error" in final_rewritten_text:
            echo_section_content("Rewriting step failed. Aborting.")
            overall_end_time = time.perf_counter()
            latency_ms = (overall_end_time - overall_start_time) * 1000
            update_metrics(latency_ms, success=False, step1=True, step2=False, step3=False)
            return None
        
        # Step 3: Extract keywords
        extracted_keywords = extract_keywords(final_rewritten_text)
        if "LLM Error" in extracted_keywords:
            echo_section_content("Keyword extraction step failed. Aborting.")
            overall_end_time = time.perf_counter()
            latency_ms = (overall_end_time - overall_start_time) * 1000
            update_metrics(latency_ms, success=False, step1=True, step2=True, step3=False)
            return None
        
        overall_end_time = time.perf_counter()
        latency_ms = (overall_end_time - overall_start_time) * 1000
        
        # Update metrics for successful completion
        update_metrics(latency_ms, success=True, step1=True, step2=True, step3=True)
        
        echo_section_header("PROCESSING COMPLETE")
        echo_section_content(f"Original Article Length: {len(article_content.split())} words")
        echo_section_content(f"Initial Summary Length: {len(initial_summary.split())} words")
        echo_section_content(f"Rewritten Summary Length: {len(final_rewritten_text.split())} words")
        echo_section_content(f"Total Processing Time: {latency_ms:.2f}ms")
        
        return {
            "summary": initial_summary,
            "rewritten": final_rewritten_text,
            "keywords": extracted_keywords
        }
    except Exception as e:
        overall_end_time = time.perf_counter()
        latency_ms = (overall_end_time - overall_start_time) * 1000
        echo_section_content(f"Error during processing: {e}")
        update_metrics(latency_ms, success=False, step1=False, step2=False, step3=False)
        return None

def main():
    echo_section_header("STARTING MULTI-STEP ARTICLE PROCESSOR")

    # Check if dashboard is running
    try:
        response = requests.get(f"{DASHBOARD_URL}/metrics", timeout=1)
        print(f"✅ Dashboard is running at {DASHBOARD_URL}")
    except:
        print(f"⚠️  Dashboard not detected at {DASHBOARD_URL}")
        print("   Metrics will still be tracked locally. Start dashboard with: ./start_dashboard.sh")

    # Load a sample article from a file
    try:
        with open("sample_article.txt", "r", encoding="utf-8") as f:
            article = f.read()
        echo_section_header("ORIGINAL ARTICLE LOADED")
        echo_section_content(article)
    except FileNotFoundError:
        echo_section_content("Error: 'sample_article.txt' not found. Please create it with some content.")
        return

    # Process the article through all steps
    result = process_article(article)
    
    if result:
        echo_section_header("FINAL RESULTS")
        echo_section_content(f"Keywords: {result['keywords']}")

if __name__ == "__main__":
    main()
