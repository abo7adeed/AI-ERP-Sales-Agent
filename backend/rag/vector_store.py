import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import chromadb
    from chromadb.errors import NotFoundError
except ImportError:
    raise ImportError(
        "chromadb is required for RAG. Install with: pip install chromadb"
    )

from backend.rag.embeddings import EmbeddingProvider

logger = logging.getLogger(__name__)

VECTOR_STORE_DIR = Path("data/vector_store")
COLLECTION_NAME = "products"


class VectorStore:
    _client = None
    _collection = None
    _lock = threading.Lock()

    @classmethod
    def _get_client(cls):
        if cls._client is None:
            VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("Initializing ChromaDB PersistentClient at %s", VECTOR_STORE_DIR)
            cls._client = chromadb.PersistentClient(path=str(VECTOR_STORE_DIR))
            logger.info("ChromaDB PersistentClient initialized")
        return cls._client

    @classmethod
    def _get_collection(cls):
        if cls._collection is None:
            with cls._lock:
                if cls._collection is not None:
                    return cls._collection
                client = cls._get_client()
                cls._collection = client.get_or_create_collection(
                    name=COLLECTION_NAME,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info("Collection '%s' initialized (count=%d)", COLLECTION_NAME, cls._collection.count())
        return cls._collection

    @classmethod
    def _build_embedding_text(cls, name: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        parts = [name]
        if description:
            parts.append(description)
        meta = metadata or {}
        specs = meta.get("specs") or meta.get("display_specs") or ""
        if specs:
            parts.append(f"المواصفات: {specs}")
        category = meta.get("category", "")
        if category:
            parts.append(f"الفئة: {category}")
        price = meta.get("price", "")
        if price:
            parts.append(f"السعر: {price}")
        return ". ".join(parts)

    @classmethod
    def add_product(
        cls,
        product_id: int,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        collection = cls._get_collection()
        text = cls._build_embedding_text(name, description, metadata)
        embedding = EmbeddingProvider.embed_text(text)
        doc_metadata = dict(metadata or {})
        doc_metadata["product_id"] = product_id
        doc_metadata["name"] = name
        collection.add(
            ids=[str(product_id)],
            embeddings=[embedding],
            documents=[text],
            metadatas=[doc_metadata],
        )
        logger.debug("Added product id=%d name=%s", product_id, name)

    @classmethod
    def add_products_batch(cls, products: List[Dict[str, Any]]):
        if not products:
            return
        collection = cls._get_collection()
        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[dict] = []

        for product in products:
            pid = product["id"]
            name = product["name"]
            description = product.get("description", "")
            meta = product.get("metadata", {})
            text = cls._build_embedding_text(name, description, meta)
            ids.append(str(pid))
            documents.append(text)
            metadatas.append({**meta, "product_id": pid, "name": name})

        all_embeddings = EmbeddingProvider.embed_texts(documents)
        collection.add(
            ids=ids,
            embeddings=all_embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        logger.info("Batch added %d products to collection '%s'", len(products), COLLECTION_NAME)

    @classmethod
    def search(cls, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        collection = cls._get_collection()
        query_embedding = EmbeddingProvider.embed_text(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            include=["documents", "metadatas", "distances"],
        )

        matches: List[Dict[str, Any]] = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i]
                similarity = max(0.0, 1.0 - distance)
                metadata = results["metadatas"][0][i]
                matches.append({
                    "id": int(doc_id),
                    "name": metadata.get("name", ""),
                    "score": round(similarity, 4),
                    "metadata": metadata,
                })

        logger.debug("Search query=%s results=%d", query, len(matches))
        return matches

    @classmethod
    def clear(cls):
        with cls._lock:
            client = cls._get_client()
            try:
                client.delete_collection(COLLECTION_NAME)
            except (ValueError, NotFoundError):
                pass
            cls._collection = None
            logger.info("Collection '%s' cleared", COLLECTION_NAME)

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        collection = cls._get_collection()
        return {
            "collection_name": COLLECTION_NAME,
            "document_count": collection.count(),
            "vector_store_path": str(VECTOR_STORE_DIR),
        }
