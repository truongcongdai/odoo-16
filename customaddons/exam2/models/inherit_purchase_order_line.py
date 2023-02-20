from odoo import models, fields, api


class InheritPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    supplier = fields.Char(string="Supplier", compute='_compute_supplier', store=True)
    product_id = fields.Many2one('product.product', domain=[('purchase_oke', '=', True)], string="Product",
                                 index='btree_not_null')

    @api.depends('product_id')
    def _compute_supplier(self):
        for rec in self:
            if rec.product_id:
                rec.supplier = ''
                supplier_line_delay = rec.product_id.seller_ids.sorted(lambda x: x.delay)
                if supplier_line_delay:
                    supplier_line_price = supplier_line_delay.sorted(lambda x: x.price)
                    supplier_name = supplier_line_price.mapped('partner_id.name')[0]
                    rec.supplier = supplier_name