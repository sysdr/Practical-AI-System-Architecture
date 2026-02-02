# Day 14: Embeddings - The Language of Semantic Search

## Overview

This project demonstrates **text embeddings** and **semantic search** - a fundamental component of Retrieval-Augmented Generation (RAG) systems. Embeddings convert text into dense vector representations that capture semantic meaning, enabling machines to understand similarity between texts beyond simple keyword matching.

## What Are Embeddings?

Embeddings are numerical vector representations of text where:
- Similar texts have vectors that are close together in vector space
- The distance/similarity between vectors indicates semantic relatedness
- Each dimension captures some aspect of meaning

```
"AI revolutionizing industries" → [0.23, -0.45, 0.67, ...] (384 dimensions)
                                          ↓
                              Similar to vectors of:
                              "Artificial intelligence transforming business"
```

## Project Structure

```
rag_system/day14_embeddings/
├── README.md           # This file
├── .gitignore          # Git ignore patterns
├── cleanup.sh          # Cleanup script for Docker and artifacts
└── src/
    ├── main.py         # Main application script
    ├── chunks.txt      # Sample text chunks for embedding
    └── requirements.txt # Python dependencies
```

## Key Components

### 1. Embedding Model
- **Model**: `all-MiniLM-L6-v2` from Sentence Transformers
- **Dimensions**: 384-dimensional vectors
- **Characteristics**: Good balance of performance and speed
- **Use Case**: Semantic similarity, clustering, search

### 2. Similarity Methods
The project demonstrates two approaches to calculate cosine similarity:

| Method | Library | Best For |
|--------|---------|----------|
| `util.cos_sim()` | sentence-transformers | Tensor inputs, GPU acceleration |
| `cosine_similarity()` | scikit-learn | NumPy arrays, educational purposes |

### 3. Sample Data
Eight diverse text chunks covering:
- Animal descriptions (fox, dog, cat)
- Technology topics (AI, deep learning, cloud computing)
- Scientific concepts (quantum physics)

## Implementation Guide

### Prerequisites
- Python 3.10+
- pip package manager
- Internet connection (for first-time model download)

### Quick Start

#### Option 1 : Manual Setup

```bash
# Navigate to project directory
cd rag_system/day14_embeddings

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r src/requirements.txt

# Run the demo
cd src
python main.py
```

#### Option 2: Using Docker

```bash
# Run setup script with Docker option
bash setup.sh
# Choose 'y' when prompted for Docker
```

### Expected Output

```
--- Day 14: Embeddings - The Language of Semantic Search ---
Loading embedding model: all-MiniLM-L6-v2...
Model loaded successfully.

Generating embeddings for 8 chunks...
Embeddings generated. Shape: torch.Size([8, 384])

--- Finding similar chunks for query: 'AI revolutionizing industries' ---

Top 3 similar chunks (using util.cos_sim):
  - Chunk: 'Artificial intelligence is transforming industries globally.'
    Similarity Score: 0.7895
  - Chunk: 'Deep learning models are at the forefront of AI innovation.'
    Similarity Score: 0.5075
  - Chunk: 'Cloud computing offers scalable and flexible infrastructure.'
    Similarity Score: 0.2419
```

## How It Works

### Step 1: Load Text Chunks
```python
text_chunks = load_chunks("chunks.txt")
# Returns: ["The quick brown fox...", "Artificial intelligence...", ...]
```

### Step 2: Generate Embeddings
```python
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(text_chunks, convert_to_tensor=True)
# Returns: tensor of shape [8, 384]
```

### Step 3: Query and Find Similar
```python
query = "AI revolutionizing industries"
query_embedding = model.encode(query, convert_to_tensor=True)
similarities = util.cos_sim(query_embedding, embeddings)
# Returns: similarity scores for each chunk
```

## Understanding Similarity Scores

| Score Range | Interpretation |
|-------------|----------------|
| 0.8 - 1.0 | Very similar / Nearly identical meaning |
| 0.6 - 0.8 | Similar / Related topics |
| 0.4 - 0.6 | Somewhat related |
| 0.2 - 0.4 | Loosely related |
| 0.0 - 0.2 | Unrelated |

## Customization

### Adding Custom Chunks
Edit `src/chunks.txt` - one text chunk per line:
```
Your custom text goes here.
Another piece of text for embedding.
Technical documentation about your domain.
```

### Adding Custom Queries
Edit `src/main.py` and add queries in the `main()` function:
```python
query_custom = "your search query here"
find_similar_chunks(query_custom, text_chunks, chunk_embeddings, model)
```

### Using Different Models
Change `EMBEDDING_MODEL_NAME` in `src/main.py`:
```python
# Options (from sentence-transformers):
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"      # Fast, 384 dims
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"     # Better quality, 768 dims
EMBEDDING_MODEL_NAME = "paraphrase-MiniLM-L6-v2"  # Paraphrase detection
```

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| sentence-transformers | 2.7.0 | Embedding model and utilities |
| numpy | 1.26.4 | Numerical operations |
| scikit-learn | 1.5.0 | Cosine similarity calculation |
| torch | 2.3.1 | Deep learning backend |

## Cleanup

To remove all generated files and Docker resources:
```bash
cd rag_system/day14_embeddings
./cleanup.sh
```

## Next Steps (Day 15)

After understanding embeddings, the next step is to store these vectors in a **Vector Database** for efficient similarity search at scale:
- Pinecone
- Weaviate
- Milvus
- ChromaDB
- FAISS

## Troubleshooting

### Model Download Issues
```bash
# Pre-download the model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### CUDA/GPU Issues
The code automatically uses CPU if CUDA is unavailable. For GPU acceleration:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Memory Issues
For large datasets, process in batches:
```python
embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)
```

## References

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [HuggingFace Model Hub](https://huggingface.co/sentence-transformers)
- [Understanding Embeddings](https://www.tensorflow.org/text/guide/word_embeddings)
- [Cosine Similarity Explained](https://en.wikipedia.org/wiki/Cosine_similarity)

## License

This project is part of the Practical AI System Architecture learning series.
