from odoo import models, fields, api


class SInheritHrDepartment(models.Model):
    _inherit = 'hr.department'

    revenue_difference = fields.Float(string='Revenue Difference', compute='_compute_revenue_difference')

    def _compute_revenue_difference(self):
        for rec in self:
            rec.revenue_difference = rec.actual_revenue - rec.spending_limit_month
