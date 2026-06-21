import logging
import re
from typing import List, Optional

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    raise ImportError(
        "sentence-transformers is required for RAG. "
        "Install with: pip install sentence-transformers"
    )

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32


class EmbeddingProvider:
    _model = None

    @classmethod
    def get_model(cls):
        if cls._model is None:
            logger.info("Loading embedding model: %s", EMBEDDING_MODEL)
            cls._model = SentenceTransformer(EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
        return cls._model

    @classmethod
    def normalize_text(cls, text: str) -> str:
        text = text.strip()
        text = re.sub(r"\s+", " ", text)
        text = text.replace("\n", " ").replace("\r", " ")
        return text

    @classmethod
    def embed_text(cls, text: str) -> List[float]:
        model = cls.get_model()
        cleaned = cls.normalize_text(text)
        embedding = model.encode(
            cleaned,
            normalize_embeddings=True,
            convert_to_tensor=False,
            show_progress_bar=False,
        )
        return embedding.tolist()

    @classmethod
    def embed_texts(
        cls, texts: List[str], batch_size: Optional[int] = None
    ) -> List[List[float]]:
        if not texts:
            return []

        model = cls.get_model()
        cleaned = [cls.normalize_text(t) for t in texts]
        embeddings = model.encode(
            cleaned,
            normalize_embeddings=True,
            convert_to_tensor=False,
            batch_size=batch_size or BATCH_SIZE,
            show_progress_bar=False,
        )
        return [emb.tolist() for emb in embeddings]
