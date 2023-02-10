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
            if i:
                sale = {
                    "name" : i.sale_team.name,
                    "actual_revenue" : i.actual_revenue,
                    "revenue_difference" : i.revenue_difference,
                }
                records_sale.append(sale)

        # lấy ra all record của hr department
        hr_department_record = self.env['hr.department'].search([])
        records_department = []
        for i in hr_department_record:
            if i:
                department = {
                    "name": i.name,
                    "actual_revenue": i.actual_revenue,
                    "revenue_difference": i.revenue_difference,
                }
                records_department.append(department)

        ctx = {
            'hr_department_record' : records_department,
            'indicator_evaluation_record' : records_sale,
            'email_to' : ';'.join(map(lambda x: x, email_accountant)),
            'email_from' : 'dai77564@st.vimaru.edu.vn',
            'send_email' : True,
            'attendee' : '',
        }
        template = self.env.ref('exam3.sale_purchase_email_template')
        template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)
