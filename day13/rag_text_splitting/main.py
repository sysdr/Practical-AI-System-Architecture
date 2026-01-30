# main.py
import os
import sys
import requests
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

console = Console()

def display_chunks(title, chunks, chunk_size, chunk_overlap):
    """Displays chunks in a professional console format."""
    console.print(Panel(
        f"[bold blue]{title}[/bold blue]\n"
        f"Chunk Size: {chunk_size}, Chunk Overlap: {chunk_overlap}",
        title_align="left",
        border_style="cyan"
    ))
    if not chunks:
        console.print("[bold yellow]No chunks generated for this configuration.[/bold yellow]")
        return
    for i, chunk in enumerate(chunks):
        chunk_text = chunk.page_content
        console.print(Panel(
            f"[bold yellow]Chunk {i+1} (Length: {len(chunk_text)})[/bold yellow]\n"
            f"{chunk_text}",
            border_style="green"
        ))
    console.print("\n")

def process_document(file_path, chunk_size=500, chunk_overlap=50):
    """Loads a document and splits it into chunks."""
    console.print(Panel(
        f"[bold magenta]Processing Document: {file_path}[/bold magenta]",
        border_style="magenta"
    ))

    documents = []
    if file_path.endswith(".txt"):
        loader = TextLoader(file_path)
    elif file_path.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    else:
        console.print(f"[bold red]Unsupported file type: {file_path}[/bold red]")
        return []
        
    try:
        documents = loader.load()
    except Exception as e:
        console.print(f"[bold red]Error loading document {file_path}: {e}[/bold red]")
        return []
    
    if not documents:
        console.print(f"[bold yellow]No content loaded from {file_path}.[/bold yellow]")
        return []

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""] # Order matters: try larger splits first
    )

    chunks = text_splitter.split_documents(documents)
    display_chunks(f"Recursive Character Splitter Results for {os.path.basename(file_path)}", chunks, chunk_size, chunk_overlap)
    return chunks

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Create sample text document if it doesn't exist
    sample_txt_path = os.path.join("data", "sample_document.txt")
    if not os.path.exists(sample_txt_path):
        with open(sample_txt_path, "w") as f:
            f.write("""# The Future of AI in Enterprise

Artificial intelligence is rapidly transforming the enterprise landscape. From automating repetitive tasks to powering advanced analytics, AI is no longer a futuristic concept but a present-day imperative. Companies are investing heavily in AI solutions to gain a competitive edge.

## Challenges and Opportunities

One of the primary challenges is data quality. AI models thrive on clean, well-structured data. Another challenge is the talent gap; skilled AI engineers are in high demand.

However, the opportunities are immense. Enhanced customer experiences, optimized supply chains, and accelerated R&D are just a few examples. The ethical implications of AI deployment also warrant careful consideration.

## RAG and the Enterprise

Retrieval-Augmented Generation (RAG) is emerging as a powerful architecture for enterprise AI. By grounding LLMs in proprietary data, RAG mitigates hallucination and provides verifiable answers. This is critical for industries like finance, healthcare, and legal, where accuracy is paramount.
""")
        console.print(f"[bold green]Created sample text document: {sample_txt_path}[/bold green]")

    # Download sample PDF if it doesn't exist
    sample_pdf_path = os.path.join("data", "sample_pdf_document.pdf")
    if not os.path.exists(sample_pdf_path):
        console.print(f"[bold yellow]Downloading sample PDF from {os.environ.get('SAMPLE_PDF_URL', 'a default URL')}...[/bold yellow]")
        try:
            pdf_url = os.environ.get('SAMPLE_PDF_URL', 'https://arxiv.org/pdf/2307.03172.pdf')
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status() # Raise an exception for HTTP errors
            with open(sample_pdf_path, 'wb') as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    pdf_file.write(chunk)
            console.print(f"[bold green]Downloaded sample PDF: {sample_pdf_path}[/bold green]")
        except requests.exceptions.RequestException as e:
            console.print(f"[bold red]Error downloading PDF: {e}. Please ensure you have internet access or provide a valid PDF URL.[/bold red]")
            sample_pdf_path = None # Mark as not available
        except Exception as e:
            console.print(f"[bold red]An unexpected error occurred during PDF download: {e}[/bold red]")
            sample_pdf_path = None

    console.print(Panel(
        "[bold green]Day 13: Text Splitting Strategies - Hands-on Experimentation[/bold green]",
        title_align="center",
        border_style="green",
        expand=False
    ))

    # Experiment 1: Standard settings for Text
    console.print(Text("\nExperiment 1: Text Document - Standard Chunk Size (200), Moderate Overlap (20)", style="bold yellow"))
    process_document(sample_txt_path, chunk_size=200, chunk_overlap=20)

    # Experiment 2: Smaller chunk size, same overlap for Text
    console.print(Text("\nExperiment 2: Text Document - Smaller Chunk Size (100), Moderate Overlap (20)", style="bold yellow"))
    process_document(sample_txt_path, chunk_size=100, chunk_overlap=20)

    # Experiment 3: Larger chunk size, larger overlap for Text
    console.print(Text("\nExperiment 3: Text Document - Larger Chunk Size (300), Larger Overlap (50)", style="bold yellow"))
    process_document(sample_txt_path, chunk_size=300, chunk_overlap=50)

    if sample_pdf_path and os.path.exists(sample_pdf_path):
        # Experiment 4: Standard settings for PDF
        console.print(Text("\nExperiment 4: PDF Document - Standard Chunk Size (500), Moderate Overlap (50)", style="bold yellow"))
        process_document(sample_pdf_path, chunk_size=500, chunk_overlap=50)

        # Experiment 5: Smaller chunk size for PDF
        console.print(Text("\nExperiment 5: PDF Document - Smaller Chunk Size (200), Moderate Overlap (20)", style="bold yellow"))
        process_document(sample_pdf_path, chunk_size=200, chunk_overlap=20)

        # Experiment 6: Larger chunk size for PDF
        console.print(Text("\nExperiment 6: PDF Document - Larger Chunk Size (800), Larger Overlap (100)", style="bold yellow"))
        process_document(sample_pdf_path, chunk_size=800, chunk_overlap=100)
    else:
        console.print("[bold red]Skipping PDF experiments as sample PDF was not available.[/bold red]")


    console.print(Panel(
        "[bold blue]Hands-on complete. Analyze the output to understand chunking behavior![/bold blue]",
        title_align="center",
        border_style="blue",
        expand=False
    ))
