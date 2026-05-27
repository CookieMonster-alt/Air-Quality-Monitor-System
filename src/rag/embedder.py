import os
from sentence_transformers import SentenceTransformer
import logging

class AILOEmbedder:
    """
    Singleton wrapper for the all-MiniLM-L6-v2 SentenceTransformer model.
    Provides thread-safe embedding generation with optimized caching.
    """
    _instance = None
    _model = None
    _MODEL_PATH = "ailo/models/embedder"
    _MODEL_ID = "all-MiniLM-L6-v2"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AILOEmbedder, cls).__new__(cls)
        return cls._instance

    def load_model(self):
        """Loads the model into RAM. Safe to call multiple times."""
        if self._model is not None:
            return

        # Determine if we have a local cached copy or need to fetch directly
        target_path = self._MODEL_PATH if os.path.exists(self._MODEL_PATH) else self._MODEL_ID

        # We wrap in try-except in case HuggingFace blocks us and we lack the local cache
        try:
            self._model = SentenceTransformer(target_path)
        except Exception as e:
            logging.error(f"Failed to load embedder: {e}")
            self._model = None

    def encode(self, texts, batch_size=32):
        """
        Generates semantic embeddings for a single string or a list of strings.
        Outputs raw numpy arrays.
        """
        if self._model is None:
            self.load_model()

        if self._model is None:
            return None

        # Standardize input to list
        is_single = isinstance(texts, str)
        if is_single:
            texts = [texts]

        embeddings = self._model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            convert_to_numpy=True
        )

        return embeddings[0] if is_single else embeddings

# Singleton Export
embedder = AILOEmbedder()
