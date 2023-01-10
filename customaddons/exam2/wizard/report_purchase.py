from odoo import models, fields, api, _
from datetime import date
class ReportPurchase(models.TransientModel):
    _name = "report.purchase"
    _description = "Report Purchase"

    month = fields.Selection([('1','January'), ('2','February'), ('3','March'),
                              ('4','April'), ('5', 'May'), ('6','June'), ('7','July'),
                              ('8','August'), ('9','September'), ('10','October'), ('11','November'), ('12','December')],
                             default=str(date.today().month), string='Month', required=True)
    department = fields.Many2many('hr.department', string="Department")

    def btn_confirm(self):
        if self.month and self.department:
            department_name = self.department.mapped('name')
            context = {
                'name': _("Detail Report"),
                'view_mode': 'tree',
                'res_model': 'hr.department',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('hr.view_department_tree').id,
                'target': 'current',
                'domain': [('name','in',department_name),('create_month', '=', self.month)],
                'context': {'create': False, 'edit': False, 'delete': False}
            }

        else:
            context = {
                'name': _('Detail Report'),
                'view_mode': 'tree',
                'res_model': 'hr.department',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('hr.view_department_tree').id,
                'target': 'current',
                'domain': [('create_month', '=',self.month)],
                'context':{'create': False, 'edit': False, 'delete': False}
            }
        return context

