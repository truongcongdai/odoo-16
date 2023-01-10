from odoo import models, fields, api


class SalesPurchase(models.Model):
    _name = 'sales.purchase'

    def btn_send_email(self):
        # lay ra ban ghi co nhom la accountant
        accountant_group_record = self.env['res.groups'].sudo().search([('name', '=', 'Accountant')])
        # lay ra id cua thuoc nhom Accountant cua res_partner
        res_users_id = accountant_group_record.users.mapped('partner_id').mapped('id')
        # lấy ra email của accountant
        email_accountant = self.env['res.partner'].search([('id', 'in', res_users_id)]).mapped('email')
        # lấy ra all record của indicator evaluation
        indicator_evaluation_record = self.env['indicator.evaluation'].search([])
        records_sale = []
        for i in indicator_evaluation_record:
            tickets_sale = {}
            if i:
                tickets_sale['name'] = i.sale_team.name
                tickets_sale['actual_revenue'] = i.actual_revenue
                tickets_sale['revenue_difference'] = i.revenue_difference
                records_sale.append(tickets_sale)
        # lấy ra all record của hr department
        hr_department_record = self.env['hr.department'].search([])
        records_department = []
        for i in hr_department_record:
            tickets_department = {}
            if i:
                tickets_department['name'] = i.name
                tickets_department['actual_revenue'] = i.actual_revenue
                tickets_department['revenue_difference'] = i.revenue_difference
                records_department.append(tickets_department)

        ctx = {}
        ctx['hr_department_record'] = records_department
        ctx['indicator_evaluation_record'] = records_sale
        ctx['email_to'] = ';'.join(map(lambda x: x, email_accountant))
        ctx['email_from'] = 'dai77564@st.vimaru.edu.vn'
        ctx['send_email'] = True
        ctx['attendee'] = ''
        template = self.env.ref('exam3.sale_purchase_email_template')
        template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)
