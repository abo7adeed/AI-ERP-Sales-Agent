"""Order service operations."""

import logging
from typing import List

from backend.services.odoo_service import OdooService
from backend.services.customer_service import CustomerService
from backend.models.order import OrderCreate, OrderLine, OrderResponse

logger = logging.getLogger(__name__)


class OrderService:
    """Service for order operations."""

    @staticmethod
    def create_order(customer_id: int, product_id: int, quantity: int = 1) -> OrderResponse:
        """
        Create a sales order/quotation in Odoo.

        Args:
            customer_id: ID of the customer
            product_id: ID of the product
            quantity: Quantity to order (default 1)

        Returns:
            OrderResponse with order details
        """
        logger.info(
            "Creating order: customer_id=%d product_id=%d qty=%d",
            customer_id,
            product_id,
            quantity,
        )

        # Verify product exists and has stock
        product = OdooService.get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Product not found: id={product_id}")

        if product.qty_available < quantity:
            raise ValueError(
                f"Insufficient stock for {product.name}: "
                f"requested={quantity}, available={product.qty_available}"
            )

        # Create order line
        line = OrderLine(
            product_id=product_id,
            quantity=quantity,
            unit_price=product.list_price,
            subtotal=product.list_price * quantity,
        )

        # Create order via Odoo service
        order = OrderCreate(customer_id=customer_id, lines=[line])
        return OdooService.create_order(order)

    @staticmethod
    def validate_order(customer_id: int, product_id: int, quantity: int = 1) -> tuple[bool, str]:
        """
        Validate order before creation.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(customer_id, int) or customer_id <= 0:
            return False, "Invalid customer ID"

        if not isinstance(product_id, int) or product_id <= 0:
            return False, "Invalid product ID"

        if not isinstance(quantity, int) or quantity <= 0:
            return False, "Invalid quantity"

        product = OdooService.get_product_by_id(product_id)
        if not product:
            return False, f"Product not found"

        if product.qty_available < quantity:
            return False, f"Insufficient stock: {product.qty_available} available"

        logger.info("Order validation passed: customer_id=%d product_id=%d qty=%d", customer_id, product_id, quantity)
        return True, ""

    @staticmethod
    def get_order_summary(order: OrderResponse) -> str:
        """
        Get human-readable order summary.

        Args:
            order: OrderResponse object

        Returns:
            Formatted order summary string
        """
        summary = (
            f"📋 ملخص الطلب\n"
            f"رقم الطلب: {order.name}\n"
            f"العميل: {order.customer_name}\n"
            f"الإجمالي: {order.total_amount} جنيه\n"
            f"الحالة: {order.status}"
        )
        return summary
