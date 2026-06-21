from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    brand_id = fields.Many2one(
        "product.brand",
        string="Brand",
        help="Mobile phone brand",
        index=True,
    )
    ram = fields.Char(string="RAM", help="e.g. 8GB, 12GB")
    storage = fields.Char(string="Storage", help="e.g. 128GB, 256GB")
    processor = fields.Char(string="Processor", help="e.g. Snapdragon 8 Gen 3")
    camera = fields.Char(string="Camera", help="e.g. 50MP, 200MP")
    battery = fields.Char(string="Battery", help="e.g. 5000mAh")
    color = fields.Char(string="Color", help="Device color")
    model_year = fields.Char(string="Model Year", help="e.g. 2024, 2025")

    display_specs = fields.Text(
        string="Specifications",
        compute="_compute_display_specs",
        store=True,
        help="Auto-generated specs summary for AI context",
    )

    @api.depends("ram", "storage", "processor", "camera", "battery", "brand_id", "model_year")
    def _compute_display_specs(self):
        for product in self:
            parts = []
            if product.brand_id:
                parts.append(f"Brand: {product.brand_id.name}")
            if product.model_year:
                parts.append(f"Model Year: {product.model_year}")
            if product.ram:
                parts.append(f"RAM: {product.ram}")
            if product.storage:
                parts.append(f"Storage: {product.storage}")
            if product.processor:
                parts.append(f"Processor: {product.processor}")
            if product.camera:
                parts.append(f"Camera: {product.camera}")
            if product.battery:
                parts.append(f"Battery: {product.battery}")
            if product.color:
                parts.append(f"Color: {product.color}")
            product.display_specs = ", ".join(parts)
