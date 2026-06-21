"""Customer service operations."""

import logging
from typing import Optional

from backend.services.odoo_service import OdooService
from backend.models.customer import CustomerCreate, CustomerResponse

logger = logging.getLogger(__name__)


class CustomerService:
    """Service for customer-related operations."""

    @staticmethod
    def get_or_create_customer(name: str, phone: str, email: Optional[str] = None) -> CustomerResponse:
        """
        Get or create a customer from Odoo.

        Args:
            name: Customer name
            phone: Customer phone number
            email: Optional customer email

        Returns:
            CustomerResponse with customer data
        """
        logger.info("Getting or creating customer: name=%s phone=%s", name, phone)

        customer = CustomerCreate(name=name, phone=phone, email=email)
        return OdooService.create_customer(customer)

    @staticmethod
    def validate_customer_data(name: str, phone: str) -> bool:
        """
        Validate customer data before creating.

        Args:
            name: Customer name
            phone: Customer phone number

        Returns:
            True if valid, False otherwise
        """
        if not name or len(name) < 2:
            logger.warning("Invalid customer name: %s", name)
            return False

        if not phone or len(phone) < 5:
            logger.warning("Invalid customer phone: %s", phone)
            return False

        return True
