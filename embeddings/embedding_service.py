"""
Simple wrapper around sentence-transformers.
This handles loading the model and generating the vector embeddings.
"""

import numpy as np
from sentence_transformers import SentenceTransformer

# We use MiniLM because it's fast and light (~80MB)
DEFAULT_MODEL = "all-MiniLM-L6-v2"

class EmbeddingService:
    def __init__(self, model_name=DEFAULT_MODEL):
        print(f"Loading embedding model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            print("Model loaded.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def embed_text(self, text):
        # Returns a 1D numpy array
        return self.model.encode(text, convert_to_numpy=True)

    def embed_texts(self, texts):
        # Batch processing - returns (N, D) array
        return self.model.encode(texts, convert_to_numpy=True)
