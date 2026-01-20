# main.py with dashboard integration
import tiktoken
import os
import requests
import time

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8080")

def update_dashboard(tokens=0, context_simulation=False, overflow=False, truncated_tokens=0, context_used=0, context_size=0, chars=0):
    """Update dashboard metrics"""
    try:
        params = {}
        if tokens > 0:
            params["tokens"] = tokens
        if context_simulation:
            params["context_simulation"] = "1"
        if overflow:
            params["overflow"] = "1"
        if truncated_tokens > 0:
            params["truncated_tokens"] = truncated_tokens
        if context_used > 0 and context_size > 0:
            params["context_used"] = context_used
            params["context_size"] = context_size
        if chars > 0 and tokens > 0:
            params["chars"] = chars
            params["tokens"] = tokens
        if params:
            requests.get(f"{DASHBOARD_URL}/update", params=params, timeout=0.1)
    except:
        pass  # Dashboard might not be running, that's okay

def count_tokens(text: str, model_name: str = "gpt-4") -> int:
    """Counts tokens for a given text using a specified model's tokenizer."""
    try:
        encoding = tiktoken.encoding_for_model(model_name)
        tokens = encoding.encode(text)
        token_count = len(tokens)
        update_dashboard(tokens=token_count, chars=len(text))
        return token_count
    except KeyError:
        print(f"Warning: Tokenizer for model '{model_name}' not found. Using 'cl100k_base' fallback.")
        encoding = tiktoken.get_encoding("cl100k_base") # Fallback for common models
        tokens = encoding.encode(text)
        token_count = len(tokens)
        update_dashboard(tokens=token_count, chars=len(text))
        return token_count

def truncate_text_to_fit_context(text: str, max_tokens: int, model_name: str = "gpt-4") -> str:
    """
    Truncates text to fit within a maximum token limit.
    Prioritizes keeping the end of the text (most recent information).
    """
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)

    if len(tokens) <= max_tokens:
        return text

    # Truncate from the beginning to fit the max_tokens
    truncated_tokens = tokens[-max_tokens:]
    truncated_text = encoding.decode(truncated_tokens)
    update_dashboard(truncated_tokens=len(tokens) - max_tokens)
    return truncated_text

def simulate_llm_interaction(input_text: str, context_window_size: int, model_name: str = "gpt-4", expected_output_tokens: int = 100):
    """
    Simulates sending text to an LLM, accounting for context window limits.
    """
    update_dashboard(context_simulation=True)
    print(f"\\n--- Simulating LLM Interaction ---")
    print(f"Model: {model_name}, Context Window: {context_window_size} tokens")
    print(f"Expected LLM Output Tokens: {expected_output_tokens}")

    # Calculate available tokens for input
    initial_input_tokens = count_tokens(input_text, model_name)
    available_input_tokens = context_window_size - expected_output_tokens
    
    if initial_input_tokens > available_input_tokens:
        print(f"\\n--- CONTEXT OVERFLOW DETECTED! ---")
        print(f"Original input ({initial_input_tokens} tokens) exceeds available input tokens ({available_input_tokens}).")
        update_dashboard(overflow=True)
        processed_input_text = truncate_text_to_fit_context(input_text, available_input_tokens, model_name)
        processed_input_tokens = count_tokens(processed_input_text, model_name) # Recount after truncation
        print(f"Text truncated to {processed_input_tokens} tokens to fit context.")
        print(f"Effective Input Text (first 200 chars): '{processed_input_text[:200]}...'")
    else:
        print(f"Input fits within context window. No truncation needed.")
        processed_input_text = input_text
        processed_input_tokens = initial_input_tokens

    total_tokens_sent = processed_input_tokens
    total_context_used = total_tokens_sent + expected_output_tokens
    print(f"\\nTokens actually sent to LLM: {total_tokens_sent} tokens")
    print(f"Total context window used (input + expected output): {total_context_used} tokens")
    
    update_dashboard(context_used=total_context_used, context_size=context_window_size)

    if total_context_used > context_window_size:
        print(f"Warning: Total context used ({total_context_used}) still exceeds context window size ({context_window_size}). This indicates an issue in calculation or aggressive output expectation.")
    else:
        print(f"Context window utilization: {total_context_used}/{context_window_size} tokens ({total_context_used/context_window_size:.2%})")

if __name__ == "__main__":
    # Check if dashboard is running
    try:
        response = requests.get(f"{DASHBOARD_URL}/metrics", timeout=1)
        print(f"✅ Dashboard is running at {DASHBOARD_URL}")
    except:
        print(f"⚠️  Dashboard not detected at {DASHBOARD_URL}")
        print("   Metrics will not be tracked. Start dashboard with: ./start_dashboard.sh")
    
    # Example texts to analyze
    short_text = "Hello, world! This is a short sentence."
    medium_text = "The quick brown fox jumps over the lazy dog. This sentence is a bit longer, designed to demonstrate how tokenization works for common English phrases. We will observe the token count closely."
    long_text = """
    In the vast expanse of the digital cosmos, where data flows like rivers of light and algorithms dance with intricate precision, a new paradigm of intelligence is rapidly emerging. Large Language Models (LLMs), once confined to the realm of theoretical computer science, have now breached the firewall of academic research and permeated the fabric of daily life. From sophisticated virtual assistants that anticipate our needs to creative writing companions that conjure narratives from thin air, LLMs are reshaping our interaction with technology.

    However, the journey from theoretical concept to practical, production-grade system is fraught with challenges. The raw power of an LLM, while awe-inspiring, comes with inherent limitations that demand careful architectural consideration. Among these, the most fundamental are the concepts of tokenization and the context window. These aren't merely technical specifications; they are the unseen boundaries that define an LLM's "memory" and, consequently, its ability to comprehend and generate coherent, relevant responses. Ignoring them is akin to designing a high-speed vehicle without understanding its fuel tank capacity or engine's RPM limits.

    As engineers and architects, our task is not just to wield these powerful tools but to master their underlying mechanics. We must understand how raw text transforms into the numerical sequences that LLMs consume, and critically, the finite capacity within which they operate. This understanding empowers us to build systems that are not only intelligent but also robust, scalable, and economically viable. Without this foundational knowledge, even the most brilliant prompt engineering can fall flat, swallowed by the silent void of context overflow, leaving users frustrated and systems unreliable. This lesson aims to demystify these core concepts, providing you with the practical insights needed to navigate the fascinating, yet challenging, landscape of LLM-powered applications.
    """
    
    # Text with a mix of languages or special characters
    mixed_text = "Hello world! Привет мир! こんにちは世界！😊 This is a test with some emojis and different scripts."

    # --- Part 1: Token Counting Analysis ---
    print("\\n--- Part 1: Token Counting Analysis ---")
    texts_to_analyze = {
        "Short Text": short_text,
        "Medium Text": medium_text,
        "Long Text": long_text,
        "Mixed Text": mixed_text
    }

    for name, text in texts_to_analyze.items():
        tokens = count_tokens(text)
        print(f"'{name}' ({len(text)} chars): {tokens} tokens")
        # Estimate character-to-token ratio (rough average)
        if tokens > 0:
            print(f"  Approx. {len(text)/tokens:.2f} chars/token")

    # --- Part 2: Context Window Simulation ---
    print("\\n--- Part 2: Context Window Simulation ---")

    # Example 1: Text fits comfortably
    print("\\n----- Scenario 1: Text Fits Comfortably -----")
    simulate_llm_interaction(short_text, context_window_size=1024)

    # Example 2: Text requires truncation
    print("\\n----- Scenario 2: Text Requires Truncation -----")
    simulate_llm_interaction(long_text, context_window_size=256) # A very small window to clearly show truncation

    # Example 3: Edge case - very small context window, output takes up most
    print("\\n----- Scenario 3: Tight Context Window -----")
    simulate_llm_interaction(medium_text, context_window_size=100, expected_output_tokens=80)

    # Example 4: Output expectation too high
    print("\\n----- Scenario 4: Output Expectation Too High -----")
    simulate_llm_interaction(short_text, context_window_size=50, expected_output_tokens=60)
    
    print("\\nDemo completed! Check dashboard at:", DASHBOARD_URL)
