import os
import streamlit as st
import shutil
from ingest import load_and_chunk_pdfs, embed_and_store, DATA_FOLDER
from rag import get_answer

# Create data folder if it doesn't exist
os.makedirs(DATA_FOLDER, exist_ok=True)

st.set_page_config(page_title="Finance RAG - Intelligence", page_icon="🏦", layout="wide")

# Custom CSS for a premium, clean dark look
st.markdown("""
<style>
    /* Main container padding */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155 !important;
    }
    
    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        background-color: #3b82f6 !important;
        color: #f8fafc !important;
        border: none !important;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
        background-color: #2563eb !important;
        color: #f8fafc !important;
    }
    
    /* Header typography */
    h1, h2, h3 {
        font-family: 'Inter', -apple-system, sans-serif;
        color: #f8fafc !important;
    }
    
    /* General text */
    p, span, div {
        color: #cbd5e1;
    }
    
    /* Source badges */
    .source-badge {
        display: inline-block;
        padding: 4px 12px;
        margin: 4px;
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 12px;
        font-size: 0.8rem;
        color: #94a3b8;
        transition: all 0.2s ease;
    }
    .source-badge:hover {
        border-color: #3b82f6;
        color: #f8fafc;
    }
    
    /* Chat message container styling */
    [data-testid="stChatMessage"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar for uploading and indexing
with st.sidebar:
    st.title("🏦 FinRAG Config")
    st.markdown("Upload quarterly financial reports to the knowledge base.")
    
    st.markdown("### 📂 Data Ingestion")
    uploaded_files = st.file_uploader("Upload Financial PDFs", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Index Files", use_container_width=True, type="primary"):
            if not uploaded_files:
                st.warning("Please upload a PDF first.")
            else:
                with st.spinner("Processing & Indexing..."):
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(DATA_FOLDER, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    chunks = load_and_chunk_pdfs(DATA_FOLDER)
                    if chunks:
                        embed_and_store(chunks)
                        st.success(f"Indexed {len(chunks)} chunks.")
                    else:
                        st.error("Extraction failed.")
    
    with col2:
        if st.button("Clear DB", use_container_width=True):
            if os.path.exists(DATA_FOLDER):
                shutil.rmtree(DATA_FOLDER)
                os.makedirs(DATA_FOLDER, exist_ok=True)
            if os.path.exists("chroma_db"):
                shutil.rmtree("chroma_db")
            st.session_state.messages = []
            st.success("Database cleared.")

    st.markdown("---")
    st.markdown("### 💡 About")
    st.info("This RAG system uses NVIDIA embeddings and Meta Llama-3.1-70B for highly accurate financial analysis. Query across multiple quarters to spot trends and extract key metrics.")

# Main area for Q&A
col1, col2, col3 = st.columns([1, 8, 1])
with col2:
    st.title("Financial Intelligence Desk")
    st.markdown("Ask natural language questions about your indexed financial reports.")
    st.markdown("---")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display sources if available for assistant messages
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander("View Sources", expanded=False):
                    for source in message["sources"]:
                        st.markdown(f"<span class='source-badge'>📄 {source['file']} (Page {source['page']})</span>", unsafe_allow_html=True)

    # Accept user input
    if prompt := st.chat_input("E.g., Compare net profit across all quarters..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            status_container = st.status("🧠 Analyzing request...", expanded=True)
            
            def update_status(msg):
                status_container.write(f"🔄 {msg}")
                
            response = get_answer(prompt, status_callback=update_status)
            status_container.update(label="✅ Analysis complete!", state="complete", expanded=False)
            
            answer_stream = response.get("answer_stream")
            sources = response.get("sources", [])
            
            if answer_stream:
                answer_text = st.write_stream(answer_stream)
            else:
                answer_text = response.get("answer", "Error: Streaming failed")
                st.markdown(answer_text)
            
            if sources:
                with st.expander("View Sources", expanded=False):
                    for source in sources:
                        st.markdown(f"<span class='source-badge'>📄 {source['file']} (Page {source['page']})</span>", unsafe_allow_html=True)
            
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": answer_text,
            "sources": sources
        })
