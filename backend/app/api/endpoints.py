from fastapi import APIRouter, UploadFile, File, Form, WebSocket, WebSocketDisconnect, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List
import shutil
import os
import uuid

from ..db.connection import get_db
from ..models.database import Collection, Document, IngestionStatus
from ..services.ingestion import IngestionService
from ..services.retrieval import RetrievalService
from ..services.llm import LLMService
import time
import json
from ..config import settings
from ..models.database import Collection, Document, IngestionStatus, Message

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

# Services (Singletons for simplicity in this scope)
ingestion_service = IngestionService()
retrieval_service = RetrievalService()
llm_service = LLMService()

# --- Page Routes ---
@router.get("/", response_class=HTMLResponse)
async def get_home(request: Request, db: Session = Depends(get_db)):
    collections = db.query(Collection).all()
    # Ensure at least one collection exists
    if not collections:
        default_col = Collection(name="Default Knowledge Base")
        db.add(default_col)
        db.commit()
        db.refresh(default_col)
        collections = [default_col]
        
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "collections": collections,
        "current_collection": collections[0]
    })

@router.get("/collections/{collection_id}", response_class=HTMLResponse)
async def get_collection_view(request: Request, collection_id: str, db: Session = Depends(get_db)):
    collections = db.query(Collection).all()
    current = db.query(Collection).filter(Collection.id == collection_id).first()
    return templates.TemplateResponse("partials/main_area.html", {
        "request": request, 
        "current_collection": current,
        "collections": collections # needed IF we re-render sidebar, but mostly for context
    })

# --- API Actions ---

@router.post("/collections")
async def create_collection(name: str = Form(...), db: Session = Depends(get_db)):
    new_col = Collection(name=name)
    db.add(new_col)
    db.commit()
    # Return sidebar partial update
    collections = db.query(Collection).all()
    return templates.TemplateResponse("partials/sidebar.html", {"request": {}, "collections": collections})

@router.post("/ingest")
async def ingest_file(
    collection_id: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. Save File Locally
    upload_dir = f"uploads/{collection_id}"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{file.filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 2. Create DB Record
    doc = Document(
        collection_id=collection_id,
        filename=file.filename,
        file_type=file.filename.split('.')[-1],
        status=IngestionStatus.PROCESSING
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # 3. Process (Ingest + Embed) - Ideally async background task
    try:
        chunks = ingestion_service.ingest(file_path, source_doc_id=doc.id)
        
        # Prepare for Vector Store
        texts = [c["text"] for c in chunks]
        metadatas = [
            {
                "collection_id": collection_id,
                "source_doc_id": doc.id,
                "filename": doc.filename,
                "page_number": c["metadata"]["page_number"]
            } 
            for c in chunks
        ]
        ids = [f"{doc.id}_{i}" for i in range(len(chunks))]
        
        retrieval_service.add_texts(texts, metadatas, ids)
        
        doc.status = IngestionStatus.DONE
        doc.token_count = sum(len(t) for t in texts) # Approx
        db.commit()
        
        return f"""<div class='text-green-500'>Successfully processed {file.filename}</div>"""
    except Exception as e:
        doc.status = IngestionStatus.FAILED
        db.commit()
        return f"""<div class='text-red-500'>Failed: {str(e)}</div>"""

# --- Chat WebSocket ---

@router.websocket("/ws/chat/{collection_id}")
async def websocket_endpoint(websocket: WebSocket, collection_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # data is the user query
            
            # 1. Save User Message
            # Note: We need a new detailed DB session or reuse the dependency if possible. 
            # However, Websocket endpoint signature in FastAPI doesn't easily support Depends(get_db) directly in the loop 
            # without some hacks or using a context manager.
            # Simplified: Create a session manually for this loop.
            
            with next(get_db()) as db:
                user_msg = Message(collection_id=collection_id, role="user", content=data)
                db.add(user_msg)
                db.commit()

                # 2. Retrieve
                chunks = retrieval_service.search(collection_id, query=data)
                
                # 3. Generate & Stream
                full_response = ""
                sources_list = []
                
                for event in llm_service.generate_response(chunks, data):
                    if event["type"] == "citation":
                        sources_list = event["data"]
                    elif event["type"] == "token":
                        full_response += event["data"]
                    await websocket.send_json(event)
                
                # 4. Save AI Message
                ai_msg = Message(
                    collection_id=collection_id, 
                    role="assistant", 
                    content=full_response,
                    sources=json.dumps(sources_list)
                )
                db.add(ai_msg)
                db.commit()
                
                # End of message signal
                await websocket.send_json({"type": "done"})
            
    except WebSocketDisconnect:
        print("Client disconnected")

@router.get("/api/test-brain")
async def test_brain():
    start = time.time()
    if not llm_service.client:
        return {"status": "offline", "error": "No API Key"}
    
    try:
        chat_completion = llm_service.client.chat.completions.create(
            messages=[{"role": "user", "content": "Hello"}],
            model=settings.GROQ_MODEL,
        )
        duration = time.time() - start
        return {
            "status": "online", 
            "response": chat_completion.choices[0].message.content,
            "latency": f"{duration:.2f}s",
            "model": settings.GROQ_MODEL
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/collections/{collection_id}/messages")
def get_messages(collection_id: str, db: Session = Depends(get_db)):
    msgs = db.query(Message).filter(Message.collection_id == collection_id).order_by(Message.created_at.asc()).all()
    return [
        {
            "id": m.id,
            "role": m.role,
            "content": m.content,
            "sources": json.loads(m.sources) if m.sources else []
        }
        for m in msgs
    ]


