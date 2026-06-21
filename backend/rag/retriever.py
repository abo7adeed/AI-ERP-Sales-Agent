import json
import logging
import threading
from pathlib import Path
from typing import Any, Dict, List

try:
    from backend.rag.vector_store import VectorStore
except ImportError:
    VectorStore = None

logger = logging.getLogger(__name__)

PRODUCTS_CATALOG_FILE = Path("data/products_catalog.json")
DEFAULT_MIN_SCORE = 0.25


class ProductRetriever:
    _initialized = False
    _init_lock = threading.Lock()

    @classmethod
    def initialize(cls, force_refresh: bool = False):
        if cls._initialized and not force_refresh:
            return
        with cls._init_lock:
            if cls._initialized and not force_refresh:
                return
            logger.info("Initializing product retriever")
            if force_refresh:
                VectorStore.clear()
            catalog_products = cls._load_catalog()
            if catalog_products:
                VectorStore.add_products_batch(catalog_products)
                cls._initialized = True
                logger.info("Product retriever initialized with %d products", len(catalog_products))
            else:
                logger.warning("No products found in catalog — retriever inactive")

    @classmethod
    def _load_catalog(cls) -> List[Dict[str, Any]]:
        if not PRODUCTS_CATALOG_FILE.exists():
            logger.warning("Catalog file not found: %s", PRODUCTS_CATALOG_FILE)
            return []
        try:
            with open(PRODUCTS_CATALOG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            products = data.get("products", [])
            logger.info("Loaded %d products from catalog", len(products))
            return products
        except Exception:
            logger.exception("Error loading products catalog")
            return []

    @classmethod
    def retrieve(
        cls,
        query: str,
        limit: int = 5,
        min_score: float = DEFAULT_MIN_SCORE,
    ) -> List[Dict[str, Any]]:
        cls.initialize()
        if VectorStore is None:
            logger.warning("VectorStore unavailable — empty retrieval")
            return []
        results = VectorStore.search(query, limit=limit)
        filtered = [r for r in results if r.get("score", 0) >= min_score]
        logger.debug(
            "Retrieved %d results (filtered from %d) for query=%s",
            len(filtered),
            len(results),
            query,
        )
        return filtered

    @classmethod
    def format_results_for_prompt(cls, results: List[Dict[str, Any]]) -> str:
        if not results:
            return ""

        lines = ['\n---', 'منتجات مقترحة لك:', '']
        for r in results:
            name = r.get("name", "Unknown")
            score = r.get("score", 0)
            meta = r.get("metadata", {})
            price = meta.get("price", "غير محدد")
            specs = meta.get("specs", meta.get("display_specs", ""))
            stock = meta.get("stock", meta.get("qty_available", ""))
            lines.append(f"• {name}  (الثقة: {score:.0%})")
            lines.append(f"  السعر: {price}")
            if stock:
                lines.append(f"  المتاح: {stock}")
            if specs:
                lines.append(f"  المواصفات: {specs}")
            lines.append("")
        lines.append("---")
        return "\n".join(lines)

    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        stats = VectorStore.get_stats()
        stats["catalog_file"] = str(PRODUCTS_CATALOG_FILE)
        stats["catalog_exists"] = PRODUCTS_CATALOG_FILE.exists()
        return stats
