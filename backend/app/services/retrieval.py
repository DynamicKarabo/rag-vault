import chromadb
from typing import List, Dict, Any
from .embedding import EmbeddingService

class RetrievalService:
    def __init__(self, persist_dir: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        # Using a single collection for all data, utilizing metadata for filtering
        self.collection = self.client.get_or_create_collection(name="rag_vectors")
        self.embedding_service = EmbeddingService()

    def add_texts(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """
        Add texts to the vector store.
        """
        embeddings = [self.embedding_service.generate_embedding(text) for text in texts]
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

    def search(self, collection_id: str, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks within a specific collection context.
        """
        query_embedding = self.embedding_service.generate_embedding(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"collection_id": collection_id} # Namespace filtering
        )
        
        # Chroma returns lists of lists (columns), let's reshape to list of dicts
        formatted_results = []
        if results['documents']:
            count = len(results['documents'][0])
            for i in range(count):
                item = {
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i] if results['metadatas'] else {},
                    "distance": results['distances'][0][i] if results['distances'] else None
                }
                formatted_results.append(item)
                
        return formatted_results
