from odoo import fields, models

class BrandTiki(models.Model):
    _name = 'brand.tiki'
    name = fields.Char(string='Tên thương hiệu')
    brand_product_id = fields.One2many('product.template','product_category_id')