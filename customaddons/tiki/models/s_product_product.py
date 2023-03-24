import base64

from odoo import fields, api, models
from odoo.exceptions import ValidationError, UserError
import json
import http.client

class SProductTemplateAttributeValue(models.Model):
    _inherit = 'product.product'

    sku = fields.Char(string='Sku',required=True)
    # image = fields.Image(string="Image",help='Product media is empty or Image size < 500 x 500 pixels')
    is_inventory_type = fields.Boolean(compute="_compute_is_inventory_type")
    warehouse_product_id = fields.One2many('warehouses.tiki.line', 'product_id_warehouses', string='Kho Tiki')

    @api.constrains('sku')
    def check_sku(self):
        sku_template_attribute_count = self.search_count([('sku', '=', self.sku)])
        sku_template_count = self.env['product.template'].search_count([('sku', '=', self.sku)])
        count_sku = sku_template_attribute_count+ sku_template_count
        if count_sku > 1:
            raise ValidationError('Sku đã được dùng. Vui lòng đổi Sku khác')

    def _compute_is_inventory_type(self):
        self.is_inventory_type = False
        for r in self:
            if r.inventory_type != 'dropship':
                r.is_inventory_type = True


