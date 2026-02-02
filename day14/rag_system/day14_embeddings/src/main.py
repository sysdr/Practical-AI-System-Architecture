# src/main.py
import os
import numpy as np
from sentence_transformers import SentenceTransformer, util
from sklearn.metrics.pairwise import cosine_similarity

# --- Configuration ---
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2" # A good balance of performance and speed
CHUNKS_FILE = "chunks.txt" # This would be the output from Day 13

# --- Helper Functions ---
def load_chunks(filepath):
    """Loads text chunks from a file, one chunk per line."""
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found. Please ensure Day 13's output is present.")
        print("Creating a dummy chunks file for demonstration.")
        with open(filepath, 'w') as f:
            f.write("The quick brown fox jumps over the lazy dog.\n")
            f.write("A fast, reddish-brown canine leaps above a sluggish hound.\n")
            f.write("Artificial intelligence is transforming industries globally.\n")
            f.write("Deep learning models are at the forefront of AI innovation.\n")
            f.write("The cat sat on the mat.\n")
        print(f"Dummy {filepath} created with example content.")
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def generate_embeddings(texts, model):
    """Generates embeddings for a list of texts."""
    print(f"\nGenerating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, convert_to_tensor=True)
    print(f"Embeddings generated. Shape: {embeddings.shape}")
    return embeddings

def find_similar_chunks(query_text, chunks, embeddings, model, top_k=3):
    """
    Finds the top_k most similar chunks to a given query text.
    Uses both util.cos_sim (HuggingFace) and sklearn.metrics.pairwise.cosine_similarity.
    """
    print(f"\n--- Finding similar chunks for query: '{query_text}' ---")
    query_embedding = model.encode(query_text, convert_to_tensor=True)

    # Method 1: Using sentence_transformers.util.cos_sim
    # This is often faster for tensor inputs
    cos_scores = util.cos_sim(query_embedding, embeddings)[0]
    top_results_idx = np.argsort(-cos_scores.cpu().numpy())[0:top_k]

    print(f"\nTop {top_k} similar chunks (using util.cos_sim):")
    for idx in top_results_idx:
        print(f"  - Chunk: '{chunks[idx]}'")
        print(f"    Similarity Score: {cos_scores[idx]:.4f}")

    # Method 2: Using sklearn.metrics.pairwise.cosine_similarity
    # Useful for demonstrating the underlying numpy operation
    sklearn_cos_scores = cosine_similarity(query_embedding.cpu().numpy().reshape(1, -1), embeddings.cpu().numpy())[0]
    sklearn_top_results_idx = np.argsort(-sklearn_cos_scores)[0:top_k]

    print(f"\nTop {top_k} similar chunks (using sklearn.metrics.pairwise.cosine_similarity):")
    for idx in sklearn_top_results_idx:
        print(f"  - Chunk: '{chunks[idx]}'")
        print(f"    Similarity Score: {sklearn_cos_scores[idx]:.4f}")


def main():
    print(f"--- Day 14: Embeddings - The Language of Semantic Search ---")
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}...")
    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure you have an internet connection or the model is cached.")
        return

    # 1. Load text chunks (simulating output from Day 13)
    text_chunks = load_chunks(CHUNKS_FILE)
    if not text_chunks:
        print("No chunks to process. Exiting.")
        return

    # 2. Generate embeddings for all chunks
    chunk_embeddings = generate_embeddings(text_chunks, model)

    # 3. Define a query and find similar chunks
    query = "AI revolutionizing industries"
    find_similar_chunks(query, text_chunks, chunk_embeddings, model)

    query_2 = "domestic animal on floor"
    find_similar_chunks(query_2, text_chunks, chunk_embeddings, model)

    query_3 = "quantum mechanics principles"
    find_similar_chunks(query_3, text_chunks, chunk_embeddings, model)

    print("\n--- Embeddings demonstration complete. ---")
    print("Next: Storing these powerful vectors in a Vector Database (Day 15).")

if __name__ == "__main__":
    main()
