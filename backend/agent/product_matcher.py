import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def find_product_in_message(message: str, products: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """
    Match a product from inventory using the user message.

    Prefers the longest product name match to avoid partial collisions.
    """
    normalized_message = _normalize_text(message)
    if not normalized_message:
        return None

    sorted_products = sorted(products, key=lambda product: len(product["name"]), reverse=True)

    for product in sorted_products:
        product_name = product["name"]
        normalized_product_name = _normalize_text(product_name)

        if normalized_product_name in normalized_message:
            logger.info("Matched product by full name: %s", product_name)
            return product

        tokens = [token for token in normalized_product_name.split() if len(token) > 1]
        if tokens and all(token in normalized_message for token in tokens):
            logger.info("Matched product by token overlap: %s", product_name)
            return product

    logger.info("No product match found in message: %s", message)
    return None
