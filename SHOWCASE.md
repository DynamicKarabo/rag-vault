# Project Showcase: RAG Vault

**"Building a Private Intelligence Agency in Code."**

This document details the engineering decisions, architecture, and skillset demonstrated in the construction of **RAG Vault**.

---

## 🏗️ What I Built

I architected and implemented a full-stack **Retrieval Augmented Generation (RAG)** application that transforms static documents into an interactive conversational intelligence. 

Instead of relying on heavy frameworks like React/Next.js, I opted for the **"Modern Monolith"** stack (**FastAPI + HTMX + Alpine.js**). This decision reduced build complexity, eliminated hydration issues, and enabled 100% server-side control over the application state while maintaining the "SPA-feel" via Websockets and partial HTML swaps.

### Key Capabilities implemented:
1.  **Ingestion Pipeline**: A factory-pattern parser that handles PDFs, DOCX, and Text, chunks them cleanly, and embeds them into a vector space.
2.  **Hybrid State Management**: 
    *   **HTMX** handles coarse-grained state (page navigation, switching collections).
    *   **Alpine.js** handles fine-grained, ephemeral state (WebSocket streaming, UI interactions, client-side animations).
3.  **Cloud-Native Integration**: Switched from local inference (Ollama) to **Groq's LPU Interface** to achieve production-grade latency, managing API keys securely via environment variables.

---

## 🧠 Skillset Demonstrated

### 1. Backend Systems Engineering (Python)
*   **FastAPI & AsyncIO**: Built high-concurrency endpoints using `async/await` to handle file I/O and WebSocket connections without blocking the main event loop.
*   **SQLAlchemy ORM**: Designed a normalized schema (`Collections` -> `Documents` -> `Messages`) with cascading deletes and UUID primary keys for scalability.
*   **Vector Database (ChromaDB)**: Implemented semantic search logic, handling embedding generation and "Where" clause filtering for multi-tenancy (Data Isolation).

### 2. Frontend Innovation
*   **The "No-Build" Stack**: Demonstrated mastery of **HTMX** and **Alpine.js** to build complex, reactive UIs without a Node.js build step or `node_modules` heaviness.
*   **WebSocket Streaming**: Implemented a real-time token stream parser that handles JSON events (`citation` vs `token` vs `error`) to render a "typing" effect identical to ChatGPT.
*   **Professional UX**: Pivoted from a niche "Cyberpunk" aesthetic to a premium "Google Material" design using **TailwindCSS**, focusing on typography, whitespace, and micro-interactions.

### 3. Application Architecture
*   **Service Layer Pattern**: Decoupled business logic (`IngestionService`, `RetrievalService`, `LLMService`) from the API routes (`endpoints.py`), ensuring code is testable and maintainable.
*   **Configuration Management**: Implemented strict environment variable handling (`pydantic-settings`) to distinguish between Dev/Prod configurations and secure secrets.

### 4. DevOps & Tooling
*   **Git Strategy**: Managed a clean version control history, utilizing `.gitignore` to prevent secret leakage and binary bloat.
*   **Dependency Management**: Maintained a precise `requirements.txt` for reproducible builds across environments.

---

## 🔮 Future Roadmap (Architecture Plan)
*   **Dockerization**: Containerize the app for one-click deployment.
*   **Multi-Modal**: Add support for Image analysis using Llama 3.2 Vision.
*   **Auth**: Implement OAuth2 for multi-user support.
