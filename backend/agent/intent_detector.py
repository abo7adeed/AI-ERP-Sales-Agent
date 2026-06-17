import logging
import re

logger = logging.getLogger(__name__)

BOOKING_KEYWORDS = (
    "احجز",
    "حجز",
    "عايز",
    "عاوز",
    "اشتري",
    "شراء",
    "book",
    "order",
    "buy",
    "reserve",
)


def has_booking_intent(message: str) -> bool:
    """Detect whether the user message expresses purchase or reservation intent."""
    normalized = message.lower()
    matched = any(keyword in normalized for keyword in BOOKING_KEYWORDS)
    logger.debug("Booking intent detected=%s for message=%s", matched, message)
    return matched
