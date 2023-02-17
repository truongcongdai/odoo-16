from odoo import models, fields, api
from odoo.exceptions import ValidationError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sale_team = fields.Many2one('crm.team', string='Sales Team')
    minimum_revenue = fields.Float(string='Minimum Revenue (VAT)' , default=0.0)
    check_priority = fields.Boolean(defult=False, compute='_compute_check_priority')
    actual_revenue = fields.Float(string='Actual Revenue', compute='_compute_actual_revenue')
    create_month = fields.Integer('Create Month', compute='_compute_create_month', store=True)


    # Tinh actual_revenue = tong amount_total_opportunity
    def _compute_actual_revenue(self):
        for rec in self:
            if rec.id:
                amount_total = self.env['sale.order'].search([('opportunity_id', '=', rec.id)])
                amount_total_opportunity = amount_total.mapped('amount_total')
                rec.actual_revenue = sum(amount_total_opportunity)

    @api.depends('create_date')
    def _compute_create_month(self):
        for rec in self:
            if rec.create_date:
                rec.create_month = rec.create_date.month

    # check priority = very high va tk có thuộc nhóm leader
    @api.depends('priority')
    def _compute_check_priority(self):
        for r in self:
            r.check_priority = False
            if (r.priority == '3' and not r.user_has_groups('exam1.group_lead_employee')) or r.priority != '3':
                r.check_priority = True

    # Kiểm tra minimum_revenue nếu nhỏ hơn 0 thì raise lỗi
    @api.onchange('minimum_revenue')
    def _check_minimum_revenue(self):
        if self.minimum_revenue < 0:
            raise ValidationError('Doanh thu tối thiểu phải lớn hơn 0')

    # chỉ assign cho nhân viên cùng nhóm còn leader assign all
    def _onchange_user_id(self):
        # lấy ra id của người dùng hiện tại
        current_user_id = self.env.uid
        # lấy ra id teamember của người dùng hiện tại
        group_staff_id = self.env['crm.team.member'].search([('user_id', '=', current_user_id)], limit=1).crm_team_id.id
        # lấy ra những tài khoản của thuộc teamember của người dùng hiện tại
        sales_staff_in_group = self.env['crm.team.member'].search([('crm_team_id', '=', group_staff_id)]).user_id.ids

        #lấy ra id của trưởng nhóm bán hàng
        id_leader = self.env['crm.team'].search([]).user_id.ids

        if current_user_id in id_leader:
            #lấy ra id của quản lý nhóm bán hàng
            manager_sales_team = self.env['crm.team'].search([('user_id', '=', current_user_id)]).ids
            #lấy ra những id nhân viên của trưởng nhóm bán hàng đó quản lý
            staff_under_manager = self.env['crm.team.member'].search([('crm_team_id', '=', manager_sales_team)]).user_id.ids
            staff_under_manager.append(current_user_id)
            return [('id', 'in', staff_under_manager)]
        else:
            return [('id', 'in', sales_staff_in_group)]

    user_id = fields.Many2one(
        'res.users', string='Salesperson', default=lambda self: self.env.user,
        domain="['&', ('share', '=', False), ('company_ids', 'in', user_company_ids)]" and _onchange_user_id,
        check_company=True, index=True, tracking=True)
