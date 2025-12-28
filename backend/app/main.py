from fastapi import FastAPI
from .db.connection import init_db

app = FastAPI(title="RAG Vault API")

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health_check():
    return {"status": "online", "version": "0.1.0"}