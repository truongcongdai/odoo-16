from odoo import models, fields, api
from odoo.exceptions import UserError


class PlanSaleOder(models.Model):
    _name = 'plan.sale.order'
    _inherit = ['mail.thread']
    name = fields.Text(string='Name', required=True)
    quotation = fields.Many2one('sale.order', string="Quotation",readonly=True)
    content = fields.Text(string="Content", required=True)
    state = fields.Selection([('new', 'New'), ('send', 'Send'), ('approve', 'Approve'), ('refuse', 'Refuse')],default='new')
    approve_id = fields.One2many('approver.list', 'sale_order_id', string='Aprrover')
    check_send = fields.Boolean(compute='_compute_check_send')

    def btn_send(self):

        #nếu mà chưa có quotation thì gán quotation = active_id
        if not self.quotation:
            self.quotation = self.env.context.get('active_id')
        # nếu state = new hoặc = refuse thì khi ấn send state = send và gửi thông báo
        if self.state == 'new' or self.state == 'refuse':
            if self.approve_id.approver:
                self.state = 'send'
                self.approve_id.approve_status = 'not_approved_yet'
                mess_send = 'kế hoạch bán hàng mới "%s" được gửi đến bạn vào ngày %s . ' % (self.name, fields.Datetime.now())
                self.message_post(partner_ids=self.approve_id.approver.ids, body=mess_send)
            else:
                raise UserError('Kế hoạch này không có bất kỳ người phê duyệt')
        else:
            raise UserError('Không thể gửi người phê duyệt này')

    # chỉ người tạo mới có thể nhìn thấy nút send
    def _compute_check_send(self):
        current_user_ui = self.env.uid
        self.check_send = False
        if current_user_ui != self.create_uid.id:
            self.check_send = True
