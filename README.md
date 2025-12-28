# RAG Vault 🧠

**RAG Vault** is a high-performance, cloud-native **Retrieval Augmented Generation (RAG)** system built for speed, accuracy, and professional usability. It allows users to create isolated "Knowledge Bases" (Collections), upload documents, and chat with them using the power of **Meta's Llama 3 70B** (via Groq).

![Status](https://img.shields.io/badge/Status-Online-success) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20HTMX%20%7C%20Alpine-purple)

## 🚀 Features

*   **Cloud-First Brain**: Powered by `llama-3.3-70b-versatile` on the **Groq LPU** for ultra-low latency inference (~300 tokens/s).
*   **Vector Search**: Uses **ChromaDB** with `all-MiniLM-L6-v2` embeddings for precise semantic retrieval.
*   **Long-Term Memory**: Full chat persistence using SQLite (users can refresh and semantic history remains).
*   **Professional UI**: A "Google-esque" clean interface built with **TailwindCSS**, featuring streaming responses, citation chips, and smooth micro-interactions.
*   **Real-Time Streaming**: Server-sent events (via WebSockets) stream the AI's thought process token-by-token.
*   **Isolated Collections**: Create distinct workspaces for different projects/topics.

## 🛠️ Technology Stack

*   **Backend**: FastAPI (Python), Uvicorn.
*   **Database**: SQLite (Metadata/History), ChromaDB (Vector Store).
*   **Frontend**: HTML5, TailwindCSS, HTMX (Server-State), Alpine.js (Client-State).
*   **AI/ML**: Groq API (LLM), Sentence-Transformers (Embeddings).

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/DynamicKarabo/rag-vault.git
cd rag-vault
```

### 2. Set up Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# Mac/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configuration
Create a `.env` file in the root directory:
```properties
GROQ_API_KEY=gsk_your_key_here
```
*(Note: You need a valid API key from console.groq.com)*

## 🏃‍♂️ Usage

### Start the Server
```bash
python -m uvicorn backend.app.main:app --reload
```

### Access the Vault
Open your browser to: **`http://127.0.0.1:8000`**

1.  **Create a Collection**: Click "New Chat" in the sidebar.
2.  **Upload Data**: Click "Upload Source" in the top header and select a PDF/TXT file.
3.  **Chat**: Ask questions based on your data.

## 🧪 Testing

Run the cloud connection diagnostic tool:
```bash
python backend/test_cloud.py
```
*Expected Output: "Status: Online", Latency < 10s.*
