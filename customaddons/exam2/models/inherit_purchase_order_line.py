from odoo import models, fields, api


class InheritPurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    supplier = fields.Char(string="Supplier", compute='_compute_supplier', store=True)
    product_id = fields.Many2one('product.product', domain=[('purchase_oke', '=', True)], string="Product",
                                 index='btree_not_null')

    # tìm supplier có gía nhỏ nhất
    # @api.depends('product_id')
    # def _compute_supplier(self):
    #     for r in self:
    #         if r.product_id:
    #             price_supplier = ''
    #             # lay ra supplier gia nho nhat
    #             price = r.product_id.seller_ids.mapped('price')
    #             if price:
    #                 min_price = min(r.product_id.seller_ids.mapped('price'))
    #                 # lay ra tên nhà san xuất co product_id=product_id.id va gia nho nhat
    #                 price_supplier = r.product_id.seller_ids.search([('price','=',min_price)]).mapped('partner_id.name')
    #             if price_supplier:
    #                 # lấy ra tên nhà san xuất có thời gian thấp nhất
    #                 shortest_delivery_time = r.product_id.seller_ids.search([('price','=',min_price)],order='delay asc', limit=1).partner_id.name
    #                 r.supplier = shortest_delivery_time
    #             else:
    #                 r.supplier = price_supplier

    @api.depends('product_id')
    def _compute_supplier(self):
        for rec in self:
            if rec.product_id:
                rec.supplier = ''
                supplier_line = rec.product_id.seller_ids
                supplier_line_delay = supplier_line.sorted(lambda x: x.delay)
                if supplier_line_delay:
                    supplier_line_price = supplier_line_delay.sorted(lambda x: x.price)
                    supplier_name = supplier_line_price.mapped('partner_id.name')[0]
                    rec.supplier = supplier_name