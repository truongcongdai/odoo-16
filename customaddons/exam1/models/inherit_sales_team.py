from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SalesTeam(models.Model):
    _inherit = 'crm.team'

    january = fields.Float(string="Tháng 1")
    february = fields.Float(string="Tháng 2")
    march = fields.Float(string="Tháng 3")
    april = fields.Float(string="Tháng 4")
    may = fields.Float(string="Tháng 5")
    june = fields.Float(string="Tháng 6")
    july = fields.Float(string="Tháng 7")
    august = fields.Float(string="Tháng 8")
    september = fields.Float(string="Tháng 9")
    october = fields.Float(string="Tháng 10")
    november = fields.Float(string="Tháng 11")
    december = fields.Float(string="Tháng 12")

    # kiểm tra tháng nếu có giá trị < 0 thì raise lỗi
    @api.constrains('january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november' , 'december')
    def _check_month(self):
        for r in self:
            if r.january <= 0 or r.february <= 0 or r.march <= 0 or r.april <= 0 or r.april <= 0 or r.may <= 0 or r.june <= 0 or r.july <= 0 or r.august <= 0 or r.september <= 0 or r.october <= 0 or r.november <= 0:
                raise ValidationError('giá trị các tháng phải lớn 0')
