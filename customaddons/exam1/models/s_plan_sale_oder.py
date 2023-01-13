from odoo import models, fields, api
from odoo.exceptions import UserError


class PlanSaleOder(models.Model):
    _name = 'plan.sale.order'
    _inherit = ['mail.thread']
    name = fields.Text(string='Name', required=True)
    quotation = fields.Many2one('sale.order', string="Quotation", readonly=True)
    content = fields.Text(string="Content", required=True)
    state = fields.Selection([('new', 'New'), ('send', 'Send'), ('approve', 'Approve'), ('refuse', 'Refuse')])
    approve_id = fields.One2many('approver.list', 'sale_order_id', string='Aprrover')
    check_send = fields.Boolean(compute='_compute_check_send')

    # khi ấn btn new thì thiết lập state = 'new' và approver_status = 'not approved yed'
    def btn_new(self):
        self.state = 'new'
        self.approve_id.approver_status = 'not approved yet'

    def btn_send(self):
        mess_send = 'kế hoạch mới đã được gửi đến approve vào ngày %s . Tạo bởi %s' % (fields.Datetime.now(), self.create_uid.name)
        # nếu state = new hoặc = refuse thì khi ấn send state = send và gửi thông báo
        if self.state == 'new' or self.state == 'refuse':
            if self.approve_id.approver:
                self.state = 'send'
                self.message_post(subject='Gửi tới người phê duyệt', body=mess_send)
            else:
                raise UserError('Kế hoạch này không có bất kỳ người phê duyệt')
        else:
            raise UserError('Không thể gửi người phê duyệt này')

    # chỉ người tạo mới có thể nhìn thấy nút send
    @api.depends('create_uid')
    def _compute_check_send(self):
        current_user_ui = self.env.uid
        self.check_send = False
        if current_user_ui != int(self.create_uid):
            self.check_send = True
