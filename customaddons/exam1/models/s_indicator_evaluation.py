from odoo import models, fields, api


class IndicatorEvaluationReport(models.Model):
    _name = 'indicator.evaluation'
    # chọn sale_team chưa có trong indicator_evaluation
    def _select_sale_team_name(self):
        id_sale_team = self.env['indicator.evaluation'].search([]).mapped('sale_team').ids
        return [('id', 'not in', id_sale_team)]

    sale_team = fields.Many2one('crm.team', string="Nhóm bán hàng", domain=_select_sale_team_name)
    actual_revenue = fields.Float(string="Doanh thu thực tế", compute="_compute_actual_revenue")
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'),
                              ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')],
                             string='Month', store=True)
    revenue_targets = fields.Float(string="Chỉ tiêu doanh thu", compute="_compute_revenue_targets", store=True)

    def _compute_actual_revenue(self):
        for rec in self:
            if rec.sale_team:
                amount_untaxed = self.env['sale.order'].search([('team_id', 'in', rec.sale_team.ids),('opportunity_id','!=',False),('state','=','sale')]).mapped('amount_untaxed')
                rec.actual_revenue = sum(amount_untaxed)

    # Tính mục tiêu doanh thu tháng để report
    @api.depends('month')
    def _compute_revenue_targets(self):
        for rec in self:
            if rec.month:
                month_sales_result = self.env['crm.team'].search([('id', 'in', rec.sale_team.mapped('id'))])
                month_sales = month_sales_result.mapped(lambda res: (res.january, res.february,
                                                                     res.march, res.april, res.may,
                                                                     res.june, res.july, res.august,
                                                                     res.september, res.october,
                                                                     res.november, res.december))
                rec.revenue_targets = month_sales[0][int(rec.month) - 1]
