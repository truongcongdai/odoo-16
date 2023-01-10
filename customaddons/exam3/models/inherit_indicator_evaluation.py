from odoo import models, fields, api
from datetime import date


class InheritIndicatorEvaluation(models.Model):
    _inherit = 'indicator.evaluation'

    revenue_difference = fields.Float(string='Revenue Difference', compute='_compute_revenue_difference')

    def _compute_revenue_difference(self):
        current_month = date.today().month

        for rec in self:
            month_sales_result = self.env['crm.team'].search([('id', 'in', rec.sale_team.mapped('id'))])
            month_sales = month_sales_result.mapped(lambda res: (res.january, res.february,
                                                                 res.march, res.april, res.may,
                                                                 res.june, res.july, res.august,
                                                                 res.september, res.october,
                                                                 res.november, res.december))
            if rec.actual_revenue:
                rec.revenue_difference = rec.actual_revenue - month_sales[0][current_month - 1]
            else:
                rec.revenue_difference = 0 - month_sales[0][current_month - 1]
