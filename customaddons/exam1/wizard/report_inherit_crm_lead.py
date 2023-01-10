from odoo import fields, models, api, _
from datetime import date


class ReportInheritCrmLead(models.TransientModel):
    _name = 'report.inherit.crm.lead'

    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'),
                              ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'),
                              ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')],
                             string='Month', default=str(date.today().month), required=True)
    sale_team = fields.Many2many('crm.team', string='Sale Team')

    # Lọc dữ liệu theo sale_team, theo tháng đã chọn hoặc theo tháng hiện tại
    def btn_confirm(self):
        if self.month and self.sale_team:
            sale_teams_id = self.sale_team.mapped('id')
            context = {
                'name': _("Detail Report"),
                'view_mode': 'tree',
                'res_model': 'crm.lead',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('crm.crm_case_tree_view_oppor').id,
                'target': 'current',
                'domain': [('team_id', 'in', sale_teams_id), ('create_month', '=', self.month)],
                'context': {'create': False, 'edit': False, 'delete': False}
            }
        else:
            context = {
                'name': _("Detail Report"),
                'view_mode': 'tree',
                'res_model': 'crm.lead',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('crm.crm_case_tree_view_oppor').id,
                'target': 'current',
                'domain': [('create_month', '=', self.month)],
                'context': {'create': False, 'edit': False, 'delete': False}
            }
        return context
