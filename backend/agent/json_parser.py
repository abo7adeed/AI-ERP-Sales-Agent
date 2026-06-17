import json
import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

JSON_BLOCK_PATTERN = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)
JSON_OBJECT_PATTERN = re.compile(r"\{[\s\S]*\}")


def _normalize_json_text(text: str) -> str:
    """Strip markdown fences and surrounding whitespace from LLM output."""
    cleaned = text.strip()
    block_match = JSON_BLOCK_PATTERN.search(cleaned)
    if block_match:
        cleaned = block_match.group(1).strip()
    else:
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
    return cleaned


def _try_parse_json(text: str) -> Optional[dict[str, Any]]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return None

    if isinstance(parsed, dict):
        return parsed
    return None


def extract_action_json(llm_response: str) -> Optional[dict[str, Any]]:
    """
    Parse agent action JSON from LLM output with multiple fallbacks.

    Handles plain JSON, markdown code blocks, and JSON embedded in extra text.
    """
    if not llm_response or not llm_response.strip():
        logger.warning("Empty LLM response received for JSON parsing")
        return None

    cleaned = _normalize_json_text(llm_response)
    logger.debug("Normalized LLM response for parsing: %s", cleaned[:500])

    parsed = _try_parse_json(cleaned)
    if parsed is not None:
        logger.info("Successfully parsed JSON action from LLM response")
        return parsed

    object_match = JSON_OBJECT_PATTERN.search(cleaned)
    if object_match:
        candidate = object_match.group(0)
        parsed = _try_parse_json(candidate)
        if parsed is not None:
            logger.info("Successfully parsed JSON action after extracting object block")
            return parsed
        logger.warning("Found JSON-like block but failed to parse: %s", candidate[:300])

    logger.warning("Could not parse JSON action from LLM response: %s", llm_response[:300])
    return None
