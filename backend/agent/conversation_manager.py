import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Directory to store conversation history
CONVERSATIONS_DIR = Path("data/conversations")


def _ensure_conversations_dir():
    """Ensure the conversations directory exists."""
    CONVERSATIONS_DIR.mkdir(parents=True, exist_ok=True)


def _get_conversation_file(user_id: str) -> Path:
    """Get the path to a user's conversation file."""
    _ensure_conversations_dir()
    return CONVERSATIONS_DIR / f"{user_id}.json"


def get_history(user_id: str, limit: int = 5) -> list[dict]:
    """
    Retrieve the last N messages from a user's conversation history.

    Args:
        user_id: Unique identifier for the user (e.g., Telegram chat_id)
        limit: Maximum number of messages to return (default 5)

    Returns:
        List of message dicts with keys: role, content, timestamp
    """
    conversation_file = _get_conversation_file(user_id)

    if not conversation_file.exists():
        logger.debug("No conversation history found for user_id=%s", user_id)
        return []

    try:
        with open(conversation_file, "r", encoding="utf-8") as f:
            messages = json.load(f)

        # Return the last `limit` messages
        recent_messages = messages[-limit:] if len(messages) > limit else messages
        logger.debug(
            "Retrieved %d messages for user_id=%s (from %d total)",
            len(recent_messages),
            user_id,
            len(messages),
        )
        return recent_messages
    except Exception as exc:
        logger.exception("Error reading conversation history for user_id=%s", user_id)
        return []


def add_message(user_id: str, role: str, content: str) -> None:
    """
    Add a message to a user's conversation history.

    Args:
        user_id: Unique identifier for the user
        role: Message role ("user" or "assistant")
        content: Message content
    """
    conversation_file = _get_conversation_file(user_id)
    _ensure_conversations_dir()

    # Load existing messages or create empty list
    messages = []
    if conversation_file.exists():
        try:
            with open(conversation_file, "r", encoding="utf-8") as f:
                messages = json.load(f)
        except Exception as exc:
            logger.warning(
                "Failed to load existing conversation for user_id=%s, starting fresh: %s",
                user_id,
                exc,
            )
            messages = []

    # Add the new message
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
    }
    messages.append(message)

    # Save updated messages
    try:
        with open(conversation_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        logger.debug(
            "Message added for user_id=%s (total messages: %d)",
            user_id,
            len(messages),
        )
    except Exception as exc:
        logger.exception("Error saving message for user_id=%s", user_id)


def clear_history(user_id: str) -> None:
    """
    Clear all conversation history for a user.

    Args:
        user_id: Unique identifier for the user
    """
    conversation_file = _get_conversation_file(user_id)

    try:
        if conversation_file.exists():
            conversation_file.unlink()
            logger.info("Cleared conversation history for user_id=%s", user_id)
    except Exception as exc:
        logger.exception("Error clearing conversation history for user_id=%s", user_id)


def format_history_for_prompt(messages: list[dict]) -> str:
    """
    Format conversation history for injection into the system prompt.

    Args:
        messages: List of message dicts from get_history()

    Returns:
        Formatted string for prompt injection
    """
    if not messages:
        return ""

    formatted = "\n---\nسياق المحادثة السابقة:\n"
    for msg in messages:
        role_label = "العميل" if msg["role"] == "user" else "المساعد"
        formatted += f"{role_label}: {msg['content']}\n"
    formatted += "---\n"

    return formatted
