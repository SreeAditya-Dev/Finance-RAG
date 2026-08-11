# Finance RAG - Quarterly Financial Reports

This repository contains a Retrieval-Augmented Generation (RAG) system built to answer questions based on quarterly financial reports. 

## 🏢 Company & Data Sources
- **Company Chosen:** `[INSERT YOUR CHOSEN COMPANY HERE, e.g., Infosys / Apple]`
- **PDF Links:**
  - `[Link to Q1 PDF]`
  - `[Link to Q2 PDF]`
  - `[Link to Q3 PDF]`

## 🚀 Setup & Run Instructions

### Prerequisites
- Python 3.10+
- NVIDIA API Key (for embeddings and LLM)

### Installation
1. Clone this repository:
   ```bash
   git clone <your-repository-url>
   cd finance-rag
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables by copying the example file:
   ```bash
   cp .env.example .env
   ```
   *Open `.env` and add your `NVIDIA_API_KEY`.*

### Running the App
**Option A: Streamlit UI**
```bash
streamlit run app.py
```
Open `http://localhost:8501` in your browser. Upload your PDFs, click "Index Documents", and start asking questions!

**Option B: FastAPI Backend (Bonus)**
```bash
uvicorn api.main:app --reload
```
Access the interactive API documentation at `http://localhost:8000/docs`.

## ⚙️ Technical Details
- **Chunk Size:** 1000 characters
- **Chunk Overlap:** 200 characters
- **Reason:** This chunk size is large enough to keep most financial tables and paragraphs intact without breaking context, while the 200-character overlap ensures no critical sentences are cut cleanly in half across chunks.
- **Embeddings:** `nvidia/nv-embedqa-e5-v5` (NVIDIA NIM API)
- **Vector DB:** ChromaDB (Persisted locally)
- **LLM:** `meta/llama-3.1-70b-instruct` (NVIDIA NIM API)

## 📸 Screenshots
*(Add screenshots of your working Streamlit application here)*
- `[Screenshot of Upload & Indexing]`
- `[Screenshot of a Question & Answer with Sources]`

## 🧪 Test Questions & Answers
*(Run your app, ask these questions, and paste the exact answers here)*

1. **What was total revenue in the most recent quarter you loaded?**
   - *Answer:* `[Paste app answer here]`
2. **Compare net profit across all the quarters you loaded. Which was highest?**
   - *Answer:* `[Paste app answer here]`
3. **How did revenue in the latest quarter compare with the same quarter of the previous year?**
   - *Answer:* `[Paste app answer here]`
4. **What did management say about the demand outlook or business environment?**
   - *Answer:* `[Paste app answer here]`
5. **Which business segment or geography grew fastest, and by how much?**
   - *Answer:* `[Paste app answer here]`
6. **What was the operating margin in each quarter, and is the trend rising or falling?**
   - *Answer:* `[Paste app answer here]`
7. **Was any dividend declared? State the amount per share and the record date.**
   - *Answer:* `[Paste app answer here]`
8. **What risks, headwinds, or challenges are mentioned in the documents?**
   - *Answer:* `[Paste app answer here]`
9. **Give me a three-line summary of the latest quarter for a client email.**
   - *Answer:* `[Paste app answer here]`
10. **What is the CEO's personal shareholding in 2015? (Trap Question)**
    - *Answer:* `[Paste app answer here - should be honest refusal]`

## 📝 What Did Not Work Well
*(Be honest about any issues you faced. Example: "PDF tables were sometimes misaligned and caused the LLM to get confused on exact margin percentages. Llama 3.1 sometimes answered slightly differently than GPT-4o would have.")*
- `[Write your honest note here]`

## 🎥 Demo Video
- `[Insert link to your 3-minute YouTube/Loom demo video]`
