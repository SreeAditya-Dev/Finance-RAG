import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List

from ingest import load_and_chunk_pdfs, embed_and_store, DATA_FOLDER, CHROMA_DB_DIR
from rag import get_answer

app = FastAPI(
    title="Finance RAG API",
    description="API for the Quarterly Financial Reports RAG System",
    version="1.0.0"
)

# Request Models
class AskRequest(BaseModel):
    question: str
    top_k: int = 4

@app.post("/ingest")
async def ingest_pdfs(files: List[UploadFile] = File(...)):
    """
    Endpoint to upload PDF files, chunk them, and store them in ChromaDB.
    """
    os.makedirs(DATA_FOLDER, exist_ok=True)
    
    saved_files = 0
    for file in files:
        if file.filename.endswith(".pdf"):
            file_path = os.path.join(DATA_FOLDER, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files += 1

    if saved_files == 0:
        raise HTTPException(status_code=400, detail="No valid PDF files uploaded.")

    # Process and store
    chunks = load_and_chunk_pdfs(DATA_FOLDER)
    if not chunks:
        raise HTTPException(status_code=500, detail="Failed to extract text from PDFs.")
        
    embed_and_store(chunks)

    return {
        "files": saved_files,
        "chunks": len(chunks)
    }

@app.post("/ask")
async def ask_question(request: AskRequest):
    """
    Endpoint to ask a question and retrieve the answer along with sources.
    """
    response = get_answer(request.question, top_k=request.top_k)
    if "answer_stream" in response:
        answer_text = "".join(list(response["answer_stream"]))
        return {
            "answer": answer_text,
            "sources": response.get("sources", [])
        }
    return response

@app.get("/stats")
async def get_stats():
    """
    Endpoint to fetch vector database and model statistics.
    """
    # Count total chunks safely
    total_chunks = 0
    if os.path.exists(CHROMA_DB_DIR):
        try:
            from langchain_chroma import Chroma
            from langchain_nvidia_ai_endpoints import NVIDIAEmbeddings
            embeddings = NVIDIAEmbeddings(model="nvidia/nv-embedqa-e5-v5")
            vectorstore = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings)
            total_chunks = len(vectorstore.get()["ids"])
        except Exception as e:
            total_chunks = f"Error reading DB: {str(e)}"

    return {
        "collection_name": "langchain",
        "total_chunks": total_chunks,
        "embedding_model": "nvidia/nv-embedqa-e5-v5 (NVIDIA NIM)",
        "llm_model": "meta/llama-3.1-70b-instruct (NVIDIA NIM)"
    }
