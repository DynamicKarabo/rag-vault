from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import uuid
import enum

Base = declarative_base()

class IngestionStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"

class Collection(Base):
    __tablename__ = "collections"
    # UUIDs are better for API security than incremental IDs
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship to docs
    documents = relationship("Document", back_populates="collection", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="collection", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String, ForeignKey("collections.id"))
    role = Column(String) # user / assistant
    content = Column(String)
    sources = Column(String, nullable=True) # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

    collection = relationship("Collection", back_populates="messages")


class Document(Base):
    __tablename__ = "documents"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    collection_id = Column(String, ForeignKey("collections.id"))
    filename = Column(String, nullable=False)
    file_type = Column(String) # pdf, txt, etc.
    status = Column(Enum(IngestionStatus), default=IngestionStatus.PENDING)
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    collection = relationship("Collection", back_populates="documents")