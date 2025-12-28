from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .db.connection import init_db
from .api.endpoints import router

app = FastAPI(title="RAG Vault API")

# Mount Static
app.mount("/static", StaticFiles(directory="backend/static"), name="static")

# Include Router
app.include_router(router)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/health")
def health_check():
    return {"status": "online", "version": "0.1.0"}