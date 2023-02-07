from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SalesTeam(models.Model):
    _inherit = 'crm.team'

    january = fields.Float(string="Tháng 1", default=0)
    february = fields.Float(string="Tháng 2", default=0)
    march = fields.Float(string="Tháng 3", default=0)
    april = fields.Float(string="Tháng 4", default=0)
    may = fields.Float(string="Tháng 5", default=0)
    june = fields.Float(string="Tháng 6", default=0)
    july = fields.Float(string="Tháng 7", default=0)
    august = fields.Float(string="Tháng 8", default=0)
    september = fields.Float(string="Tháng 9", default=0)
    october = fields.Float(string="Tháng 10", default=0)
    november = fields.Float(string="Tháng 11", default=0)
    december = fields.Float(string="Tháng 12", default=0)
    currency_id = fields.Many2one('res.currency', string='Currency',readonly=False, store=True)

    # kiểm tra tháng nếu có giá trị < 0 thì raise lỗi
    @api.onchange('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november' , 'december')
    def _check_month(self):
        for r in self:
            if r.january < 0 or r.february < 0 or r.march < 0 or r.april < 0 or r.april < 0 or r.may < 0 or r.june < 0 or r.july < 0 or r.august < 0 or r.september < 0 or r.october < 0 or r.november < 0:
                raise ValidationError('giá trị các tháng phải lớn 0')
