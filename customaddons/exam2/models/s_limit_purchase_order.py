from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LimitPurchaseOrder(models.Model):
    _name = 'limit.purchase.order'

    name = fields.Many2one('res.users', string="Staff's Name")
    order_limit = fields.Float(string="Order Limit")

    # kiểm tra order limit nếu < 0 thì raise lỗi
    @api.constrains('order_limit')
    def _check_order_limit(self):
        if self.order_limit <= 0:
            raise ValidationError('Giới hạn đặt hàng phải lớn hơn 0')


class LimitPurchase(models.Model):
    _name = 'limit.purchase'

    limit_purchase_ids = fields.Many2many('limit.purchase.order', string="Limit Purchase Order")
