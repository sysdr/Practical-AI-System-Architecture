import os
import json
import time
import glob as glob_module
from datetime import datetime
from langchain_community.document_loaders import TextLoader, DirectoryLoader, PyPDFLoader, WebBaseLoader
from langchain_core.documents import Document

METRICS_FILE = "metrics.json"

def init_metrics():
    """Initialize metrics file with default values"""
    return {
        "text_documents_loaded": 0,
        "pdf_documents_loaded": 0,
        "web_documents_loaded": 0,
        "total_documents_loaded": 0,
        "total_characters_processed": 0,
        "load_time_text_ms": 0,
        "load_time_pdf_ms": 0,
        "load_time_web_ms": 0,
        "total_load_time_ms": 0,
        "last_update": None,
        "errors": 0,
        "success_rate": 0.0,
        "documents_per_type": {"text": 0, "pdf": 0, "web": 0}
    }

def save_metrics(metrics):
    """Save metrics to JSON file"""
    metrics["last_update"] = datetime.now().isoformat()
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)
    return metrics

def load_metrics():
    """Load existing metrics or create new"""
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, 'r') as f:
            return json.load(f)
    return init_metrics()

def run_document_loader_demo():
    """Main document loader demonstration with metrics collection"""
    metrics = init_metrics()
    total_chars = 0
    total_operations = 0
    successful_operations = 0
    
    print("--- RAG Document Loader Demo ---")
    print("This script demonstrates loading documents from local text, local PDF, and a web URL.")

    # --- 1. Load from Local Text File(s) ---
    print("\n[STEP 1] Loading from local text files in 'data/' directory...")
    total_operations += 1
    try:
        start_time = time.time()
        text_documents = []
        # Use TextLoader directly for each .txt file (more reliable than DirectoryLoader)
        txt_files = glob_module.glob('./data/**/*.txt', recursive=True)
        for txt_file in txt_files:
            try:
                loader = TextLoader(txt_file, encoding='utf-8')
                text_documents.extend(loader.load())
            except Exception as file_error:
                print(f"  Warning: Could not load {txt_file}: {file_error}")
        load_time = int((time.time() - start_time) * 1000)
        
        metrics["text_documents_loaded"] = len(text_documents)
        metrics["load_time_text_ms"] = load_time
        metrics["documents_per_type"]["text"] = len(text_documents)
        
        print(f"Loaded {len(text_documents)} text document(s) in {load_time}ms.")
        for i, doc in enumerate(text_documents):
            total_chars += len(doc.page_content)
            print(f"  Text Document {i+1}:")
            print(f"    Source: {doc.metadata.get('source', 'N/A')}")
            content_preview = doc.page_content[:200] if len(doc.page_content) > 200 else doc.page_content
            print(f"    Content (first 200 chars): {content_preview}...")
            print(f"    Metadata: {doc.metadata}")
        successful_operations += 1
    except Exception as e:
        print(f"  Failed to load local text files: {e}")
        metrics["errors"] += 1

    # --- 2. Load from Local PDF File(s) ---
    print("\n[STEP 2] Loading from local PDF files in 'data/' directory...")
    total_operations += 1
    try:
        start_time = time.time()
        pdf_loader = DirectoryLoader(
            './data/',
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True,
            silent_errors=True
        )
        pdf_documents = pdf_loader.load()
        load_time = int((time.time() - start_time) * 1000)
        
        metrics["pdf_documents_loaded"] = len(pdf_documents)
        metrics["load_time_pdf_ms"] = load_time
        metrics["documents_per_type"]["pdf"] = len(pdf_documents)
        
        print(f"Loaded {len(pdf_documents)} PDF document(s) in {load_time}ms.")
        for i, doc in enumerate(pdf_documents):
            total_chars += len(doc.page_content)
            print(f"  PDF Document {i+1}:")
            print(f"    Source: {doc.metadata.get('source', 'N/A')}")
            print(f"    Content (first 200 chars): {doc.page_content[:200]}...")
            print(f"    Metadata: {doc.metadata}")
        successful_operations += 1
    except Exception as e:
        print(f"  Failed to load local PDF files: {e}")
        metrics["errors"] += 1

    # --- 3. Load from a Web URL ---
    web_url = os.getenv("WEB_URL", "https://www.paulgraham.com/greatwork.html")
    print(f"\n[STEP 3] Loading from a web URL: {web_url}")
    total_operations += 1
    try:
        start_time = time.time()
        web_loader = WebBaseLoader(web_url)
        web_documents = web_loader.load()
        load_time = int((time.time() - start_time) * 1000)
        
        metrics["web_documents_loaded"] = len(web_documents)
        metrics["load_time_web_ms"] = load_time
        metrics["documents_per_type"]["web"] = len(web_documents)
        
        print(f"Loaded {len(web_documents)} web document(s) from {web_url} in {load_time}ms.")
        for i, doc in enumerate(web_documents):
            total_chars += len(doc.page_content)
            print(f"  Web Document {i+1}:")
            print(f"    Source: {doc.metadata.get('source', 'N/A')}")
            print(f"    Content (first 200 chars): {doc.page_content[:200]}...")
            print(f"    Metadata: {doc.metadata}")
        successful_operations += 1
    except Exception as e:
        print(f"  Failed to load web URL {web_url}: {e}")
        print("  This might be due to network issues, the URL being inaccessible/invalid, or parsing errors.")
        metrics["errors"] += 1

    # Calculate final metrics
    metrics["total_documents_loaded"] = (
        metrics["text_documents_loaded"] + 
        metrics["pdf_documents_loaded"] + 
        metrics["web_documents_loaded"]
    )
    metrics["total_characters_processed"] = total_chars
    metrics["total_load_time_ms"] = (
        metrics["load_time_text_ms"] + 
        metrics["load_time_pdf_ms"] + 
        metrics["load_time_web_ms"]
    )
    metrics["success_rate"] = round((successful_operations / total_operations) * 100, 2) if total_operations > 0 else 0

    # Save metrics
    save_metrics(metrics)
    
    print("\n--- Document Loader Demo Complete ---")
    print(f"\n=== METRICS SUMMARY ===")
    print(f"Total Documents Loaded: {metrics['total_documents_loaded']}")
    print(f"  - Text: {metrics['text_documents_loaded']}")
    print(f"  - PDF: {metrics['pdf_documents_loaded']}")
    print(f"  - Web: {metrics['web_documents_loaded']}")
    print(f"Total Characters Processed: {metrics['total_characters_processed']}")
    print(f"Total Load Time: {metrics['total_load_time_ms']}ms")
    print(f"Success Rate: {metrics['success_rate']}%")
    print(f"Metrics saved to: {METRICS_FILE}")
    
    return metrics

if __name__ == "__main__":
    run_document_loader_demo()
