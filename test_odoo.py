"""Tests for Odoo service layer (mocked)."""

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent))

from backend.models.product import Product
from backend.models.customer import CustomerCreate, CustomerResponse
from backend.services.odoo_service import OdooService


@patch("backend.services.odoo_service.check_stock_and_prices")
def test_get_products(mock_check_stock):
    """Test retrieving products from Odoo."""
    mock_check_stock.return_value = [
        {
            "id": 1,
            "name": "iPhone 14",
            "list_price": 5000,
            "qty_available": 10,
            "description_sale": "Test phone",
            "default_code": "IPHONE-14",
        }
    ]

    # Clear cache first
    OdooService.clear_product_cache()

    products = OdooService.get_products()

    assert len(products) == 1
    assert products[0].id == 1
    assert products[0].name == "iPhone 14"
    assert products[0].list_price == 5000


@patch("backend.services.odoo_service.check_stock_and_prices")
def test_get_product_by_id(mock_check_stock):
    """Test retrieving a specific product by ID."""
    mock_check_stock.return_value = [
        {"id": 1, "name": "iPhone 14", "list_price": 5000, "qty_available": 10},
        {"id": 2, "name": "Samsung S23", "list_price": 4500, "qty_available": 5},
    ]

    OdooService.clear_product_cache()

    product = OdooService.get_product_by_id(1)

    assert product is not None
    assert product.id == 1
    assert product.name == "iPhone 14"


@patch("backend.services.odoo_service.check_stock_and_prices")
def test_get_product_by_id_not_found(mock_check_stock):
    """Test retrieving a non-existent product."""
    mock_check_stock.return_value = [
        {"id": 1, "name": "iPhone 14", "list_price": 5000, "qty_available": 10},
    ]

    OdooService.clear_product_cache()

    product = OdooService.get_product_by_id(999)

    assert product is None


@patch("backend.services.odoo_service.check_stock_and_prices")
def test_search_products(mock_check_stock):
    """Test searching for products by name."""
    mock_check_stock.return_value = [
        {
            "id": 1,
            "name": "iPhone 14 Pro",
            "list_price": 5000,
            "qty_available": 10,
            "description_sale": "Premium iPhone",
        },
        {
            "id": 2,
            "name": "Samsung Galaxy S23",
            "list_price": 4500,
            "qty_available": 5,
            "description_sale": "Premium Android",
        },
    ]

    OdooService.clear_product_cache()

    results = OdooService.search_products("iPhone", limit=10)

    assert len(results) == 1
    assert results[0].name == "iPhone 14 Pro"


@patch("backend.services.odoo_service.search_or_create_customer")
def test_create_customer(mock_search_or_create):
    """Test creating a customer."""
    mock_search_or_create.return_value = 123

    customer = CustomerCreate(name="أحمد علي", phone="+201001234567", email="ahmed@example.com")
    response = OdooService.create_customer(customer)

    assert response.id == 123
    assert response.name == "أحمد علي"
    assert response.phone == "+201001234567"


if __name__ == "__main__":
    print("[TEST] Odoo Service Tests (Mocked)")
    print("=" * 50)

    try:
        test_get_products()
        print("[PASS] test_get_products")

        test_get_product_by_id()
        print("[PASS] test_get_product_by_id")

        test_get_product_by_id_not_found()
        print("[PASS] test_get_product_by_id_not_found")

        test_search_products()
        print("[PASS] test_search_products")

        test_create_customer()
        print("[PASS] test_create_customer")

        print("=" * 50)
        print("[OK] All Odoo service tests passed!")

    except AssertionError as e:
        print(f"[FAIL] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
