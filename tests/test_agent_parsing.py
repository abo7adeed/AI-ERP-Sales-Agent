import json

import pytest

from backend.agent.intent_detector import has_booking_intent
from backend.agent.json_parser import extract_action_json
from backend.agent.product_matcher import find_product_in_message, _build_product_search_text
from backend.agent.prompts import SALES_AGENT_PROMPT_TEMPLATE


SAMPLE_PRODUCTS = [
    {"id": 16, "name": "Honor 200", "list_price": 15000, "qty_available": 20},
    {"id": 17, "name": "Honor X8b", "list_price": 12000, "qty_available": 20},
    {"id": 5, "name": "Redmi Note 13", "list_price": 9000, "qty_available": 10},
]

SAMPLE_PRODUCTS_WITH_SPECS = [
    {
        "id": 16,
        "name": "Honor 200",
        "list_price": 15000,
        "qty_available": 20,
        "ram": "12GB",
        "storage": "256GB",
        "processor": "Snapdragon 7 Gen 3",
        "camera": "50MP Studio Portrait",
        "battery": "5200mAh",
        "color": "Emerald Green",
        "display_specs": "Brand: Honor, RAM: 12GB, Storage: 256GB, Processor: Snapdragon 7 Gen 3, Camera: 50MP Studio Portrait, Battery: 5200mAh, Color: Emerald Green",
    },
    {
        "id": 7,
        "name": "Xiaomi 14T Pro",
        "list_price": 29000,
        "qty_available": 5,
        "ram": "12GB",
        "storage": "512GB",
        "processor": "Dimensity 9300+",
        "camera": "50MP Leica Lens",
        "battery": "5000mAh",
        "color": "Titan Black",
        "display_specs": "Brand: Xiaomi, RAM: 12GB, Storage: 512GB, Processor: Dimensity 9300+, Camera: 50MP Leica Lens, Battery: 5000mAh, Color: Titan Black",
    },
    {
        "id": 9,
        "name": "Realme GT 6T",
        "list_price": 18000,
        "qty_available": 8,
        "ram": "12GB",
        "storage": "256GB",
        "processor": "Snapdragon 7+ Gen 3",
        "camera": "50MP",
        "battery": "5500mAh",
        "color": "Fluid Silver",
        "display_specs": "Brand: Realme, RAM: 12GB, Storage: 256GB, Processor: Snapdragon 7+ Gen 3, Camera: 50MP, Battery: 5500mAh, Color: Fluid Silver",
    },
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


def test_find_product_by_spec_ram():
    matched = find_product_in_message("مطلوب موبايل 12GB رام ومعالج Dimensity", SAMPLE_PRODUCTS_WITH_SPECS)
    assert matched is not None
    assert matched["name"] == "Xiaomi 14T Pro"


def test_find_product_by_spec_processor():
    matched = find_product_in_message("عايز حاجة بمعالج Dimensity", SAMPLE_PRODUCTS_WITH_SPECS)
    assert matched is not None
    assert matched["name"] == "Xiaomi 14T Pro"


def test_find_product_by_spec_storage():
    matched = find_product_in_message("دور على موبايل تخزين 512", SAMPLE_PRODUCTS_WITH_SPECS)
    assert matched is not None
    assert matched["name"] == "Xiaomi 14T Pro"


def test_build_product_search_text_includes_specs():
    product = {
        "name": "Test Phone",
        "ram": "8GB",
        "storage": "128GB",
        "processor": "Snapdragon",
        "camera": "50MP",
        "battery": "5000mAh",
        "color": "Black",
    }
    text = _build_product_search_text(product)
    assert "8GB" in text
    assert "128GB" in text
    assert "Snapdragon" in text
    assert "50MP" in text
    assert "5000mAh" in text
    assert "Black" in text


def test_find_product_no_match_returns_none():
    matched = find_product_in_message("أريد تابلت", SAMPLE_PRODUCTS_WITH_SPECS)
    assert matched is None
