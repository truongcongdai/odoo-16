import werkzeug.wrappers
from odoo.exceptions import ValidationError

from odoo import http
from odoo.http import request
import json


class ApiReport(http.Controller):
    @http.route('/api-report', auth='none', type="json", methods=["POST"], csrf=False)
    def controllerapi(self):
        body = json.loads(request.httprequest.data)
        token = "odooneverdie"
        if not body.get('token'):
            raise ValidationError('Chưa có key token trong body!')
        if not body.get('month'):
            raise ValidationError('Chưa có key month trong body!')
        if body.get('token') == token:
            data = {
                "sales": [],
                "purchase": [],
            }
            # lấy ra all record của indicator evaluation với supperuser với create_month = month
            indicator_evaluation_record = request.env['indicator.evaluation'].sudo().search(
                [('month', '=', body["month"])])
            for rec in indicator_evaluation_record:
                if rec:
                    data['sales'].append({
                        'name': rec.sale_team.name,
                        'actual_revenue': rec.actual_revenue,
                        'revenue_difference': rec.revenue_difference,
                    })
            # lấy ra all record của hr department với supperuser với create_month = month
            hr_department_record = request.env['hr.department'].sudo().search([('create_month', '=', body["month"])])
            for rec in hr_department_record:
                if rec:
                    data['purchase'].append({
                        'name': rec.name,
                        'actual_revenue': rec.actual_revenue,
                        'revenue_difference': rec.revenue_difference,
                    })

            return data