"""Tests for sales agent module."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))

from backend.agent.sales_agent import _build_inventory_context
from backend.models.product import Product


def test_build_inventory_context():
    """Test building inventory context from products."""
    products = [
        Product(
            id=1,
            name="iPhone 14 Pro",
            list_price=5000,
            qty_available=10,
            description_sale="أحدث جهاز من أبل",
        ),
        Product(
            id=2,
            name="Samsung Galaxy S23",
            list_price=4500,
            qty_available=5,
            description_sale="أقوى هاتف أندرويد",
        ),
    ]

    context = _build_inventory_context(products)

    assert "الموبايلات المتاحة في المخزن حالياً" in context
    assert "iPhone 14 Pro" in context
    assert "Samsung Galaxy S23" in context
    assert "5000" in context
    assert "4500" in context
    assert "10" in context
    assert "5" in context


def test_build_inventory_context_empty():
    """Test with empty product list."""
    products = []
    context = _build_inventory_context(products)

    assert "الموبايلات المتاحة في المخزن حالياً" in context


def test_build_inventory_context_no_description():
    """Test with product that has no description."""
    products = [
        Product(
            id=1,
            name="Test Phone",
            list_price=2000,
            qty_available=3,
            description_sale=None,
        ),
    ]

    context = _build_inventory_context(products)

    assert "Test Phone" in context
    assert "لا توجد مواصفات" in context


if __name__ == "__main__":
    print("[TEST] Sales Agent Tests")
    print("=" * 50)

    try:
        test_build_inventory_context()
        print("[PASS] test_build_inventory_context")

        test_build_inventory_context_empty()
        print("[PASS] test_build_inventory_context_empty")

        test_build_inventory_context_no_description()
        print("[PASS] test_build_inventory_context_no_description")

        print("=" * 50)
        print("[OK] All agent tests passed!")

    except AssertionError as e:
        print(f"[FAIL] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
