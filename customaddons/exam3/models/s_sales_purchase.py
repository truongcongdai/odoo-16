from odoo import models, fields, api


class SalesPurchase(models.Model):
    _name = 'sales.purchase'

    def btn_send_email(self):
        # lấy ra email của accountant
        email_accountant = self.env.ref('exam2.group_accountant_staff').users.mapped('email')
        # lấy ra all record của indicator evaluation
        indicator_evaluation_record = self.env['indicator.evaluation'].search([])
        records_sale = []
        for rec in indicator_evaluation_record:
            if rec:
                sale = {
                    "name" : rec.sale_team.name,
                    "actual_revenue" : rec.actual_revenue,
                    "revenue_difference" : rec.revenue_difference,
                }
                records_sale.append(sale)

        # lấy ra all record của hr department
        hr_department_record = self.env['hr.department'].search([])
        records_department = []
        for rec in hr_department_record:
            if rec:
                department = {
                    "name": rec.name,
                    "actual_revenue": rec.actual_revenue,
                    "revenue_difference": rec.revenue_difference,
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
