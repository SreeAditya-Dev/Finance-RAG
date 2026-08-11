import os
from dotenv import load_dotenv
from langchain_nvidia_ai_endpoints import ChatNVIDIA, NVIDIAEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

CHROMA_DB_DIR = "chroma_db"

def get_answer(query: str, persist_directory: str = CHROMA_DB_DIR, top_k: int = 20, status_callback=None):
    """
    Retrieves the most relevant chunks for a given query from ChromaDB 
    and uses GPT-4o to generate a response.
    """
    if status_callback: status_callback("Initializing embeddings & vector store...")
    # 1. Initialize Embeddings and Vector DB
    embeddings = NVIDIAEmbeddings(model="nvidia/nv-embedqa-e5-v5")
    
    # Check if vectorstore exists
    if not os.path.exists(persist_directory):
        return {
            "answer": "Error: Vector database not found. Please upload and index documents first.",
            "sources": []
        }
        
    vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})

    if status_callback: status_callback("Retrieving relevant documents from database...")
    # 2. Retrieve relevant chunks
    retrieved_docs = retriever.invoke(query)
    
    if not retrieved_docs:
        return {
            "answer": "No relevant context found in the uploaded documents.",
            "sources": []
        }

    if status_callback: status_callback(f"Found {len(retrieved_docs)} document chunks. Constructing context...")
    # 3. Construct context and sources
    context_text = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
    
    # Format sources with file name and page number
    sources = []
    for doc in retrieved_docs:
        # PyPDFLoader usually stores file path in 'source' and page number in 'page'
        file_path = doc.metadata.get("source", "Unknown file")
        file_name = os.path.basename(file_path)
        page_num = doc.metadata.get("page", 0) + 1  # 0-indexed in pypdf
        sources.append({"file": file_name, "page": page_num})
        
    # Deduplicate sources while preserving order
    unique_sources = []
    for s in sources:
        if s not in unique_sources:
            unique_sources.append(s)

    if status_callback: status_callback("Setting up LLM and generating response...")
    # 4. Set up the LLM (NVIDIA NIM Llama-3.1-70B) and System Prompt
    llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct", temperature=0.1, timeout=120)

    system_prompt = (
        "You are an assistant for a research desk of an investment advisory firm.\n"
        "Answer the question ONLY based on the context provided below.\n"
        "If the context does not contain the answer, reply exactly with: "
        "'The information is not available in the uploaded documents.'\n"
        "Do not invent or guess any figures or information.\n\n"
        "Context:\n"
        "{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}"),
    ])

    if status_callback: status_callback("Synthesizing final answer...")
    # 5. Generate Answer
    chain = prompt | llm
    
    def response_generator():
        for chunk in chain.stream({"context": context_text, "question": query}):
            yield chunk.content

    return {
        "answer_stream": response_generator(),
        "sources": unique_sources
    }

if __name__ == "__main__":
    # Small test script (will only work if ChromaDB has data)
    test_q = "Compare net profit across all the quarters you loaded. Which was highest?"
    print(f"Question: {test_q}\n")
    res = get_answer(test_q)
    print("Answer:")
    print(res["answer"])
    print("\nSources:")
    print(res["sources"])
