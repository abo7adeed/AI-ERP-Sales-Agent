import json

import pytest

from backend.agent.intent_detector import has_booking_intent
from backend.agent.json_parser import extract_action_json
from backend.agent.product_matcher import find_product_in_message
from backend.agent.prompts import SALES_AGENT_PROMPT_TEMPLATE


SAMPLE_PRODUCTS = [
    {"id": 16, "name": "Honor 200", "list_price": 15000, "qty_available": 20},
    {"id": 17, "name": "Honor X8b", "list_price": 12000, "qty_available": 20},
    {"id": 5, "name": "Redmi Note 13", "list_price": 9000, "qty_available": 10},
]


def test_prompt_template_formats_without_key_error():
    rendered = SALES_AGENT_PROMPT_TEMPLATE.format(context="sample inventory")
    assert "sample inventory" in rendered
    assert '"action": "create_order"' in rendered


@pytest.mark.parametrize(
    "raw_response,expected_action,expected_product_id",
    [
        (
            '{"action": "create_order", "product_id": 16, "reply": "تمام يا فندم"}',
            "create_order",
            16,
        ),
        (
            '```json\n{"action": "create_order", "product_id": 22, "reply": "حاضر"}\n```',
            "create_order",
            22,
        ),
        (
            'Here is the order:\n{"action": "create_order", "product_id": 9, "reply": "تم الحجز"}\nThanks!',
            "create_order",
            9,
        ),
    ],
)
def test_extract_action_json_success(raw_response, expected_action, expected_product_id):
    parsed = extract_action_json(raw_response)
    assert parsed is not None
    assert parsed["action"] == expected_action
    assert parsed["product_id"] == expected_product_id


def test_extract_action_json_returns_none_for_plain_text():
    parsed = extract_action_json("أهلاً يا فندم، إزيك النهاردة؟")
    assert parsed is None


def test_extract_action_json_returns_none_for_invalid_json():
    parsed = extract_action_json('{"action": "create_order", product_id: 16}')
    assert parsed is None


def test_has_booking_intent_for_arabic_message():
    assert has_booking_intent("عايز احجز Honor 200") is True


def test_find_product_in_message_matches_honor_200():
    matched = find_product_in_message("عايز احجز Honor 200", SAMPLE_PRODUCTS)
    assert matched is not None
    assert matched["id"] == 16
    assert matched["name"] == "Honor 200"
