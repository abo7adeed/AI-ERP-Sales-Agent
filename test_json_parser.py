"""Tests for JSON parser module."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.agent.json_parser import extract_action_json


def test_extract_action_json_create_order():
    """Test extracting create_order action."""
    text = 'بناءً على طلبك، سأقوم بحجز الآيفون 14 لك.\n```json\n{"action": "create_order", "product_id": 1, "reply": "تم حجز الآيفون 14 بنجاح"}\n```'

    action = extract_action_json(text)
    assert action is not None, "Should extract action from text"
    assert action.get("action") == "create_order"
    assert action.get("product_id") == 1


def test_extract_action_json_no_action():
    """Test when no action JSON is present."""
    text = "السلام عليكم، لدينا عدة موبايلات متاحة للاختيار من بينها"

    action = extract_action_json(text)
    assert action is None, "Should return None when no action JSON found"


def test_extract_action_json_invalid_json():
    """Test when JSON block is present but invalid."""
    text = "```json\n{invalid json}\n```"

    action = extract_action_json(text)
    assert action is None, "Should return None for invalid JSON"


def test_extract_action_json_multiple_blocks():
    """Test when multiple code blocks exist, should extract first JSON."""
    text = (
        "بعض النصوص\n"
        "```json\n"
        '{"action": "create_order", "product_id": 5}\n'
        "```\n"
        "نصوص إضافية"
    )

    action = extract_action_json(text)
    assert action is not None
    assert action.get("action") == "create_order"
    assert action.get("product_id") == 5


if __name__ == "__main__":
    print("[TEST] JSON Parser Tests")
    print("=" * 50)

    try:
        test_extract_action_json_create_order()
        print("[PASS] test_extract_action_json_create_order")

        test_extract_action_json_no_action()
        print("[PASS] test_extract_action_json_no_action")

        test_extract_action_json_invalid_json()
        print("[PASS] test_extract_action_json_invalid_json")

        test_extract_action_json_multiple_blocks()
        print("[PASS] test_extract_action_json_multiple_blocks")

        print("=" * 50)
        print("[OK] All JSON parser tests passed!")

    except AssertionError as e:
        print(f"[FAIL] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
