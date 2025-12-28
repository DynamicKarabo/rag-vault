import os
import json
from typing import List, Dict, Any, Generator
import httpx

# Try importing Groq, but don't fail if installed but not configured yet
try:
    from groq import Groq
except ImportError:
    Groq = None

class LLMService:
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.groq_api_key and Groq:
            self.client = Groq(api_key=self.groq_api_key)
            
    def _format_prompt(self, context: str, question: str) -> List[Dict[str, str]]:
        return [
            {"role": "system", "content": "You are a helpful assistant. Answer the user's question based ONLY on the provided context. If the answer is not in the context, say 'I cannot find the answer in the provided documents.'"},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]

    def _get_unique_sources(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        sources = {}
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            # Use source_doc_id + page as unique key
            src_id = meta.get("source_doc_id", "unknown")
            page = meta.get("page_number", "?")
            key = f"{src_id}_{page}"
            
            if key not in sources:
                sources[key] = {
                    "source_doc_id": src_id,
                    "page_number": page,
                    # Fallback if filename isn't in metadata yet (ingestion might need update to include it)
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
        
        # 3. Call LLM
        # Priority: Groq -> Ollama
        response_generated = False
        
        if self.client:
            try:
                stream = self.client.chat.completions.create(
                    messages=messages,
                    model="llama3-8b-8192",
                    stream=True
                )
                for chunk in stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield {"type": "token", "data": content}
                response_generated = True
            except Exception as e:
                print(f"Groq Error: {e}")
                # Fallback continues below
        
        if not response_generated:
            print("Attempting Fallback to Ollama...")
            try:
                # Ollama API structure
                payload = {
                    "model": "llama3", # User must have this pulled
                    "messages": messages,
                    "stream": True # Ollama streams by default usually, but explicit is good
                }
                
                # Using httpx for streaming
                with httpx.stream("POST", "http://localhost:11434/api/chat", json=payload, timeout=60.0) as r:
                    if r.status_code != 200:
                        yield {"type": "error", "data": f"Ollama Error: {r.status_code} - {r.read().decode()}"}
                        return

                    for line in r.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                msg = data.get("message", {})
                                content = msg.get("content", "")
                                if content:
                                    yield {"type": "token", "data": content}
                                if data.get("done", False):
                                    break
                            except json.JSONDecodeError:
                                pass
            except Exception as e:
                yield {"type": "error", "data": f"All LLMs failed. Groq/Ollama unreachable. Error: {e}"}
