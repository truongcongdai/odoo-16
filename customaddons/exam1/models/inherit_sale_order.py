from odoo import fields, api, models
from odoo.exceptions import ValidationError


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'
    plan_sale_order_id = fields.Many2one('plan.sale.order', string='Plan Sale Order')

    # Ghi đè kiểm tra kế hoạch đã thêm và kế hoạch đã được phê duyệt
    def action_confirm(self):
        if self.plan_sale_order_id and self.plan_sale_order_id.state == 'approve':
            return super(InheritSaleOrder, self).action_confirm()
        else:
            raise ValidationError('Kế hoạch kinh doanh chưa được bổ sung hoặc phê duyệt')
