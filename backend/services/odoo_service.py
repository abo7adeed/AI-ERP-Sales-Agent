"""Odoo integration service with caching."""

import logging
from functools import lru_cache
from typing import List, Dict, Any

from backend.tools.odoo_tools import (
    check_stock_and_prices,
    create_sales_quotation,
    search_or_create_customer,
)
from backend.models.product import Product
from backend.models.customer import CustomerCreate, CustomerResponse
from backend.models.order import OrderCreate, OrderResponse

logger = logging.getLogger(__name__)


class OdooService:
    """Service layer for Odoo operations with caching."""

    @staticmethod
    @lru_cache(maxsize=128)
    def get_products() -> List[Product]:
        """
        Get all available products from Odoo inventory.
        Results are cached for performance.
        """
        logger.info("Fetching products from Odoo inventory")
        try:
            products_data = check_stock_and_prices()
            products = [
                Product(
                    id=p["id"],
                    name=p["name"],
                    list_price=p.get("list_price", 0),
                    qty_available=int(p.get("qty_available", 0)),
                    description_sale=p.get("description_sale"),
                    display_specs=p.get("display_specs"),
                    brand_id=p.get("brand_id") and p["brand_id"][0] if isinstance(p.get("brand_id"), list) else p.get("brand_id"),
                    ram=p.get("ram"),
                    storage=p.get("storage"),
                    processor=p.get("processor"),
                    camera=p.get("camera"),
                    battery=p.get("battery"),
                    color=p.get("color"),
                    sku=p.get("default_code"),
                )
                for p in products_data
            ]
            logger.info("Retrieved %d products from Odoo", len(products))
            return products
        except Exception as exc:
            logger.exception("Error fetching products from Odoo")
            raise

    @staticmethod
    @lru_cache(maxsize=256)
    def get_product_by_id(product_id: int) -> Product | None:
        """
        Get a specific product by ID.
        Results are cached.
        """
        products = OdooService.get_products()
        for product in products:
            if product.id == product_id:
                logger.debug("Found product: %s (id=%d)", product.name, product_id)
                return product
        logger.warning("Product not found: id=%d", product_id)
        return None

    @staticmethod
    def search_products(query: str, limit: int = 10) -> List[Product]:
        """
        Search for products by name or description.
        Not cached as queries are usually unique.
        """
        logger.info("Searching for products: query=%s limit=%d", query, limit)
        products = OdooService.get_products()
        query_lower = query.lower()

        matching = [
            p for p in products
            if query_lower in p.name.lower()
            or (p.description_sale and query_lower in p.description_sale.lower())
        ]

        result = matching[:limit]
        logger.info("Found %d matching products", len(result))
        return result

    @staticmethod
    def create_customer(customer: CustomerCreate) -> CustomerResponse:
        """
        Create or retrieve a customer from Odoo.
        """
        logger.info("Creating/retrieving customer: name=%s phone=%s", customer.name, customer.phone)
        try:
            customer_id = search_or_create_customer(customer.name, customer.phone)
            logger.info("Customer resolved: id=%d", customer_id)

            return CustomerResponse(
                id=customer_id,
                name=customer.name,
                phone=customer.phone,
                email=customer.email,
            )
        except Exception as exc:
            logger.exception("Error creating customer")
            raise

    @staticmethod
    def create_order(order: OrderCreate) -> OrderResponse:
        """
        Create a sales order in Odoo.
        For now, supports single-line orders (common for this bot).
        """
        logger.info("Creating order: customer_id=%d lines=%d", order.customer_id, len(order.lines))

        if not order.lines:
            raise ValueError("Order must have at least one line")

        # For this implementation, create one order per line
        # In a real system, you'd create a single order with multiple lines
        line = order.lines[0]
        try:
            order_name = create_sales_quotation(order.customer_id, line.product_id, qty=line.quantity)
            logger.info("Created quotation: %s", order_name)

            return OrderResponse(
                id=1,  # Would need to fetch actual ID from Odoo
                name=order_name,
                customer_id=order.customer_id,
                customer_name="",  # Would fetch from DB
                total_amount=line.subtotal,
                status="draft",
                lines=order.lines,
            )
        except Exception as exc:
            logger.exception("Error creating order")
            raise

    @staticmethod
    def clear_product_cache():
        """Clear the product cache. Useful for testing or manual refresh."""
        logger.info("Clearing product cache")
        OdooService.get_products.cache_clear()
        OdooService.get_product_by_id.cache_clear()

    @staticmethod
    def get_cache_info() -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        return {
            "get_products": OdooService.get_products.cache_info()._asdict(),
            "get_product_by_id": OdooService.get_product_by_id.cache_info()._asdict(),
        }
