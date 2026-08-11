import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
from langchain_chroma import Chroma

# Load environment variables (API key)
load_dotenv()

DATA_FOLDER = "data"
CHROMA_DB_DIR = "chroma_db"

def load_and_chunk_pdfs(data_folder: str = DATA_FOLDER):
    """
    Loads all PDF files from the data folder and splits them into chunks.
    """
    print(f"Loading PDFs from '{data_folder}'...")
    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the data folder.")
        return []

    documents = []
    for pdf_path in pdf_files:
        print(f"Processing {pdf_path}...")
        loader = PyPDFLoader(pdf_path)
        documents.extend(loader.load())
        
    print(f"Loaded {len(documents)} pages in total.")

    # Chunking: Recursive character splitting
    # Size 1000 characters, overlap 200 characters per assignment requirements
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    
    print("Chunking documents...")
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    
    return chunks

def embed_and_store(chunks, persist_directory: str = CHROMA_DB_DIR):
    """
    Creates embeddings for the chunks and stores them in ChromaDB.
    """
    if not chunks:
        print("No chunks to process. Exiting.")
        return None

    print("Generating embeddings and initializing Chroma DB...")
    # Using NVIDIA NIM embedding model
    embeddings = NVIDIAEmbeddings(model="NV-Embed-QA")
    
    # Store in ChromaDB, persisted to disk
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    
    print(f"Successfully stored vectors in '{persist_directory}' directory.")
    return vectorstore

def main():
    chunks = load_and_chunk_pdfs()
    if chunks:
        embed_and_store(chunks)

if __name__ == "__main__":
    main()
