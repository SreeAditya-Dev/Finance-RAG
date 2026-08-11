import os
import streamlit as st
import shutil
from ingest import load_and_chunk_pdfs, embed_and_store, DATA_FOLDER
from rag import get_answer

# Create data folder if it doesn't exist
os.makedirs(DATA_FOLDER, exist_ok=True)

st.set_page_config(page_title="Finance RAG - Quarterly Reports", page_icon="📈", layout="centered")

st.title("📈 Finance RAG for Quarterly Reports")
st.markdown("Upload your company's quarterly financial PDFs and ask questions.")

# Sidebar for uploading and indexing
with st.sidebar:
    st.header("1. Upload & Index")
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    
    if st.button("Index Documents"):
        if not uploaded_files:
            st.warning("Please upload at least one PDF file first.")
        else:
            with st.spinner("Processing files..."):
                # Save uploaded files to the data directory
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(DATA_FOLDER, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # Run ingest pipeline
                chunks = load_and_chunk_pdfs(DATA_FOLDER)
                if chunks:
                    embed_and_store(chunks)
                    st.success(f"{len(uploaded_files)} files processed, {len(chunks)} chunks stored.")
                else:
                    st.error("No text could be extracted from the PDFs.")

    st.markdown("---")
    if st.button("Clear Data (Reset)"):
        # Helper to clear data
        if os.path.exists(DATA_FOLDER):
            shutil.rmtree(DATA_FOLDER)
            os.makedirs(DATA_FOLDER, exist_ok=True)
        if os.path.exists("chroma_db"):
            shutil.rmtree("chroma_db")
        st.success("All data cleared. You can start fresh.")

# Main area for Q&A
st.header("2. Ask a Question")
question = st.text_input("Enter your question about the financial reports:")

if st.button("Ask"):
    if not question:
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching for answers..."):
            response = get_answer(question)
            
            st.markdown("### Answer")
            st.info(response["answer"])
            
            # Display sources
            if response["sources"]:
                st.markdown("### Sources")
                for source in response["sources"]:
                    st.caption(f"📄 **File:** {source['file']} | **Page:** {source['page']}")
