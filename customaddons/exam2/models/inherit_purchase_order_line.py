from odoo import models, fields, api


class InheritPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    supplier = fields.Char(string="Supplier", compute='_compute_supplier', store=True)
    product_id = fields.Many2one('product.product', domain=[('purchase_oke', '=', True)], string="Product",
                                 index='btree_not_null')

    # tìm supplier có gía nhỏ nhất
    @api.depends('product_id')
    def _compute_supplier(self):
        for r in self:
            if r.product_id:
                # lay ra supplier gia nho nhat
                min_price = self.env['product.supplierinfo'].search(
                    [('product_tmpl_id', '=', int(r.product_id.product_tmpl_id))], order='price asc', limit=1).price

                # lay ra tên nhà san xuất co product_tmpl_id=product_id.product_tmpl_id va gia nho nhat
                price_supplier = self.env['product.supplierinfo'].search(
                    [('product_tmpl_id', '=', int(r.product_id.product_tmpl_id)), ('price', '=', min_price)],
                    order='price asc').mapped('partner_id.name')
                if len(price_supplier) > 1:
                    # lấy ra tên nhà san xuất có thời gian thấp nhất
                    shortest_delivery_time = self.env['product.supplierinfo'].search(
                        [('product_tmpl_id', '=', int(r.product_id.product_tmpl_id)), ('price', '=', min_price)],
                        order='delay asc', limit=1).mapped('partner_id.name')
                    r.supplier = ''.join(shortest_delivery_time)
                else:
                    r.supplier = ''.join(price_supplier)
