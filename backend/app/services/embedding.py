from sentence_transformers import SentenceTransformer
from typing import List

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        # This will download the model on first use if not present
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a vector embedding for the given text.
        """
        if not text:
            return []
        
        # encode returns a numpy array, convert to list for JSON/Chroma validation
        embedding = self.model.encode(text)
        return embedding.tolist()
