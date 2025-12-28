import json
from typing import List, Dict, Any, Generator
from groq import Groq
from ..config import settings

class LLMService:
    def __init__(self):
        self.client = None
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
        else:
            print("WARNING: GROQ_API_KEY not found. LLM features will fail.")

    def _format_prompt(self, context: str, question: str) -> List[Dict[str, str]]:
        return [
            {
                "role": "system", 
                "content": "You are a helpful assistant. Use the provided context to answer the user's question. If the answer is not in the context, strictly say 'I don't have that information in the Vault'."
            },
            {
                "role": "user", 
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ]

    def _get_unique_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = {}
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            src_id = meta.get("source_doc_id", "unknown")
            page = meta.get("page_number", "?")
            key = f"{src_id}_{page}"
            
            if key not in sources:
                sources[key] = {
                    "source_doc_id": src_id,
                    "page_number": page,
                    "filename": meta.get("filename", f"doc-{src_id}") 
                }
        return list(sources.values())

    def generate_response(self, chunks: List[Dict[str, Any]], question: str) -> Generator[Dict[str, Any], None, None]:
        """
        Yields:
        - {"type": "citation", "data": [...]}
        - {"type": "token", "data": "..."}
        """
        # 1. Yield Sources
        sources = self._get_unique_sources(chunks)
        yield {
            "type": "citation",
            "data": sources
        }
        
        # 2. Prepare Prompt
        context_text = "\n\n".join([c["text"] for c in chunks])
        messages = self._format_prompt(context_text, question)
        
        # 3. Call Groq
        if not self.client:
            yield {"type": "error", "data": "System Error: Brain Offline (Missing API Key)."}
            return

        try:
            stream = self.client.chat.completions.create(
                messages=messages,
                model=settings.GROQ_MODEL,
                stream=True
            )
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield {"type": "token", "data": content}
        except Exception as e:
            print(f"Groq Error: {e}")
            yield {"type": "error", "data": f"Connection to Brain Failed: {str(e)}"}
