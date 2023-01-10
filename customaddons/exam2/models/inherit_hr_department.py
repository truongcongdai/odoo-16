from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InheritHrDepartment(models.Model):
    _inherit = 'hr.department'

    spending_limit_month = fields.Float(string="Spending Limit Month")
    actual_revenue = fields.Float(string='Actual Revenue', compute='_compute_actual_revenue')
    create_month = fields.Integer(string='Create Month', compute='_compute_create_month', store=True)

    # kiểm tra spending_limit_month nếu < 0 thì raise lỗi
    @api.constrains('spending_limit_month')
    def _check_spending_limit_month(self):
        if self.spending_limit_month <= 0:
            raise ValidationError('Giới hạn chi tiêu tháng phải lớn hơn 0')

    # Tính tổng doanh thu thực tế
    def _compute_actual_revenue(self):
        for rec in self:
            if rec.name:
                amount_total = self.env['purchase.order'].search([('department', '=', rec.id)])
                amount_total_department = amount_total.mapped('amount_total')
                rec.actual_revenue = sum(amount_total_department)

    @api.depends('create_date')
    def _compute_create_month(self):
        for rec in self:
            if rec.create_date:
                rec.create_month = rec.create_date.month
