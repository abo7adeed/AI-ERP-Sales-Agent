"""RAG (Retrieval-Augmented Generation) module."""

import logging

logger = logging.getLogger(__name__)

# Try to import RAG components; these require optional dependencies
try:
    from backend.rag.embeddings import EmbeddingProvider
except ImportError as e:
    logger.warning("RAG embeddings not available: %s", e)
    EmbeddingProvider = None

try:
    from backend.rag.vector_store import VectorStore
except ImportError as e:
    logger.warning("RAG vector store not available: %s", e)
    VectorStore = None

try:
    from backend.rag.retriever import ProductRetriever
except ImportError as e:
    logger.warning("RAG retriever not available: %s", e)
    ProductRetriever = None

__all__ = [
    "EmbeddingProvider",
    "VectorStore",
    "ProductRetriever",
]
