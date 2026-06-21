{
    "name": "Mobile Store AI",
    "version": "17.0.1.0.0",
    "category": "Sales",
    "summary": "Mobile phone sales management with AI assistant integration",
    "description": """
        Extends Odoo products with mobile phone-specific fields (brand, RAM, storage,
        camera, battery, processor, color) and provides integration hooks for the
        AI-powered Telegram sales assistant.
    """,
    "author": "Mobile Store AI",
    "depends": ["sale", "stock", "product"],
    "data": [
        "security/ir.model.access.csv",
        "data/product_brand_data.xml",
        "views/product_brand_views.xml",
        "views/product_template_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
