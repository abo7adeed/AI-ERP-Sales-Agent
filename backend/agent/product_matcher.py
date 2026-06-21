import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _build_product_search_text(product: dict[str, Any]) -> str:
    """Build a rich search text from product fields."""
    parts = [product.get("name", "")]
    for field in ("ram", "storage", "processor", "camera", "battery", "color", "display_specs"):
        val = product.get(field)
        if val:
            parts.append(str(val))
    brand = product.get("brand_id")
    if isinstance(brand, (list, tuple)) and len(brand) > 1:
        parts.append(str(brand[1]))
    return " ".join(parts)


def _normalize_value(val: str) -> str:
    """Strip common units and normalize for comparison."""
    text = val.lower().strip()
    for unit in ["gb", "mah", "mp", "mm", "kg", "w", "v"]:
        for suffix in [unit, f"-{unit}"]:
            if text.endswith(suffix) and len(text) > len(suffix):
                text = text[:-len(suffix)].strip()
                break
    return text


def _extract_numbers(text: str) -> set[str]:
    """Extract numeric values from text."""
    return set(re.findall(r"\d+", text))


def _count_spec_matches(message: str, product: dict[str, Any]) -> int:
    """Count spec field tokens from the product that appear in the message."""
    normalized_message = _normalize_text(message)
    message_numbers = _extract_numbers(normalized_message)
    score = 0
    for field in ("ram", "storage", "processor", "camera", "battery", "color"):
        val = product.get(field)
        if not val:
            continue
        normalized_val = _normalize_text(val)
        if normalized_val in normalized_message:
            score += 2  # full value match is strongest
            continue
        # Check individual tokens
        for token in normalized_val.split():
            if len(token) > 1 and token in normalized_message:
                score += 1
                break
        else:
            # Check if numbers in the value appear in the message (unit-agnostic)
            val_numbers = _extract_numbers(normalized_val)
            if val_numbers and val_numbers & message_numbers:
                score += 1
    return score


def find_product_in_message(message: str, products: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    """
    Match a product from inventory using the user message.

    Prefers the longest product name match to avoid partial collisions.
    Falls back to matching individual spec field values against the message.
    """
    normalized_message = _normalize_text(message)
    if not normalized_message:
        return None

    # 1. Exact name match (highest priority)
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

    # 2. Spec value matching — find product with most matching spec fields
    best_product = None
    best_score = 0
    for product in sorted_products:
        score = _count_spec_matches(message, product)
        if score > best_score:
            best_score = score
            best_product = product

    if best_score > 0:
        logger.info("Matched product by spec fields (score=%d): %s", best_score, best_product["name"])
        return best_product

    logger.info("No product match found in message: %s", message)
    return None
