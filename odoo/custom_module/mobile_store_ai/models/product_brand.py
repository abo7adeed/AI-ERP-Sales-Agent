from odoo import fields, models


class ProductBrand(models.Model):
    _name = "product.brand"
    _description = "Mobile Phone Brand"
    _order = "name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Brand Name", required=True, translate=True)
    code = fields.Char(string="Brand Code", required=True)
    description = fields.Text(string="Description", translate=True)
    logo = fields.Binary(string="Logo", attachment=True)
    website = fields.Char(string="Website")
    product_count = fields.Integer(
        string="Product Count",
        compute="_compute_product_count",
    )

    def _compute_product_count(self):
        product_data = self.env["product.template"]._read_group(
            [("brand_id", "in", self.ids)],
            ["brand_id"],
            ["__count"],
        )
        counts = {p["brand_id"][0]: p["brand_id_count"] for p in product_data}
        for brand in self:
            brand.product_count = counts.get(brand.id, 0)
