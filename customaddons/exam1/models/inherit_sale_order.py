from odoo import fields, api, models
from odoo.exceptions import ValidationError


class InheritSaleOrder(models.Model):
    _inherit = 'sale.order'

    plan_sale_order_id = fields.Many2one('plan.sale.order', string='Plan Sale Order')
    check_plan_sale_order = fields.Boolean(default=False,compute='_compute_check_plan_sale_order',readonly=False)

    # Ghi đè kiểm tra kế hoạch đã thêm và kế hoạch đã được phê duyệt
    def action_confirm(self):
        if self.plan_sale_order_id and self.plan_sale_order_id.state == 'approve':
            return super(InheritSaleOrder, self).action_confirm()
        else:
            raise ValidationError('Kế hoạch kinh doanh chưa được bổ sung hoặc phê duyệt')

    def create_plan_sale_order(self):
        return {
            'name': self.partner_id.name,
            'view_mode': 'form',
            'res_model': 'plan.sale.order',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('exam1.plan_sale_order_view_form').id,
            'target': 'current',
        }

    def _compute_check_plan_sale_order(self):
        if self.id:
            self.check_plan_sale_order = True
