import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from .chunking import RecursiveCharacterTextSplitter
import PyPDF2
from docx import Document as DocxDocument
import typing

# Define the output object structure
class IngestedChunk(typing.TypedDict):
    text: str
    metadata: Dict[str, Any]

class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str, source_doc_id: str) -> List[IngestedChunk]:
        pass

class PDFParser(BaseParser):
    def parse(self, file_path: str, source_doc_id: str) -> List[IngestedChunk]:
        chunks: List[IngestedChunk] = []
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        # We return partial chunks (pages) to be split further? 
                        # Or do we treat the whole doc as one?
                        # User requirement: "output of the ingestion service is a list of objects containing the chunk text and metadata (source_doc_id, page_number)"
                        # So we should probably preserve page numbers if we can.
                        chunks.append({
                            "text": text,
                            "metadata": {
                                "source_doc_id": source_doc_id, 
                                "page_number": page_num + 1
                            }
                        })
        except Exception as e:
            print(f"Error parsing PDF {file_path}: {e}")
        return chunks

class DocxParser(BaseParser):
    def parse(self, file_path: str, source_doc_id: str) -> List[IngestedChunk]:
        chunks: List[IngestedChunk] = []
        try:
            doc = DocxDocument(file_path)
            # DOCX doesn't have strict "pages" like PDF. We'll treat paragraphs or the whole thing.
            # To provide granular metadata, we might group paragraphs? 
            # For simplicity, we'll extract all text and set page_number to 1 (or 0).
            full_text = "\n".join([para.text for para in doc.paragraphs])
            chunks.append({
                "text": full_text,
                "metadata": {
                    "source_doc_id": source_doc_id,
                    "page_number": 1 # DOCX flowable
                }
            })
        except Exception as e:
            print(f"Error parsing DOCX {file_path}: {e}")
        return chunks

class TextParser(BaseParser):
    def parse(self, file_path: str, source_doc_id: str) -> List[IngestedChunk]:
        chunks: List[IngestedChunk] = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                chunks.append({
                   "text": text,
                   "metadata": {
                       "source_doc_id": source_doc_id,
                       "page_number": 1
                   }
                })
        except Exception as e:
            print(f"Error parsing Text {file_path}: {e}")
        return chunks

class ParserFactory:
    @staticmethod
    def get_parser(file_path: str) -> BaseParser:
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext == '.pdf':
            return PDFParser()
        elif ext == '.docx':
            return DocxParser()
        elif ext in ['.txt', '.md']:
            return TextParser()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

class IngestionService:
    def __init__(self):
        self.chunker = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=102)

    def ingest(self, file_path: str, source_doc_id: str) -> List[IngestedChunk]:
        parser = ParserFactory.get_parser(file_path)
        # 1. Parse raw text-chunks (pages or full docs)
        raw_chunks = parser.parse(file_path, source_doc_id)
        
        final_output: List[IngestedChunk] = []
        
        # 2. Split into smaller chunks
        for raw in raw_chunks:
            splits = self.chunker.split_text(raw['text'])
            base_metadata = raw['metadata']
            
            for split in splits:
                final_output.append({
                    "text": split,
                    "metadata": base_metadata # Inherit metadata (e.g. page number)
                })
                
        return final_output
