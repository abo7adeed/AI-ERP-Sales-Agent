import logging
import xmlrpc.client

from backend.config import ODOO_DB, ODOO_PASSWORD, ODOO_URL, ODOO_USERNAME

logger = logging.getLogger(__name__)

# Connect to Odoo 17 via XML-RPC
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

logger.info("Connected to Odoo at %s db=%s uid=%s", ODOO_URL, ODOO_DB, uid)

def check_stock_and_prices():
    """Fetch available products, prices, and specs from Odoo"""
    logger.debug("Fetching saleable products from Odoo")
    product_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, "product.product", "search", [[["sale_ok", "=", True]]]
    )
    phones = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "product.product",
        "read",
        [product_ids],
        {"fields": ["name", "list_price", "qty_available", "description_sale"]},
    )
    logger.info("Fetched %d products from Odoo", len(phones))
    return phones

def search_or_create_customer(name: str, phone: str) -> int:
    """Lookup customer by phone, create a new record if not found"""
    logger.info("Searching customer by phone=%s", phone)
    customer_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD, "res.partner", "search", [[["phone", "=", phone]]]
    )

    if customer_ids:
        logger.info("Found existing customer_id=%s", customer_ids[0])
        return customer_ids[0]

    customer_id = models.execute_kw(
        ODOO_DB,
        uid,
        ODOO_PASSWORD,
        "res.partner",
        "create",
        [{"name": name, "phone": phone}],
    )
    logger.info("Created new customer_id=%s name=%s", customer_id, name)
    return customer_id

def create_sales_quotation(customer_id: int, product_id: int, qty: int = 1) -> str:
    """Create a new sales quotation (Draft Order) in Odoo"""
    try:
        logger.info(
            "Creating quotation customer_id=%s product_id=%s qty=%s",
            customer_id,
            product_id,
            qty,
        )
        order_id = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "sale.order",
            "create",
            [{"partner_id": customer_id}],
        )

        product = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "product.product",
            "read",
            [[product_id]],
            {"fields": ["name"]},
        )
        product_name = product[0]["name"] if product else "Mobile Device"

        models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "sale.order.line",
            "create",
            [
                {
                    "order_id": order_id,
                    "product_id": product_id,
                    "product_uom_qty": qty,
                    "name": product_name,
                }
            ],
        )

        order_data = models.execute_kw(
            ODOO_DB,
            uid,
            ODOO_PASSWORD,
            "sale.order",
            "read",
            [[order_id]],
            {"fields": ["name"]},
        )
        order_name = order_data[0]["name"]
        logger.info("Quotation created successfully: %s", order_name)
        return order_name
    except Exception as e:
        logger.exception("Failed to create quotation in Odoo")
        return f"Error creating quotation: {str(e)}"