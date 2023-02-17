from odoo import models, fields
from odoo.exceptions import UserError


class ApproverList(models.Model):
    _name = 'approver.list'

    approver = fields.Many2one('res.partner', string='Approver')
    approve_status = fields.Selection(
        [('not_approved_yet', 'Not Approved Yet'),
         ('approve', 'Approve'),
         ('refuse', 'Refuse')], default='not_approved_yet', string='Approver Status', readonly=True)
    check_approve = fields.Boolean(compute='_compute_check_approve')
    sale_order_id = fields.Many2one('plan.sale.order', string='Plan Sale Order')

    def btn_approve(self):
        mess_approve = 'Kế hoạch mới "%s" của bạn đã được phê duyệt vào %s' % (self.sale_order_id.name,fields.Datetime.now())
        if self.sale_order_id.state == 'send':
            self.approve_status = 'approve'
            # lấy ra all status của danh sách người phê duyệt
            states = self.sale_order_id.approve_id.mapped('approve_status')
            # nếu tất cả người đều phê duyệt thì state = approve và gửi thông báo
            if all([state == 'approve' for state in states]):
                self.sale_order_id.state = 'approve'
                self.sale_order_id.message_post(partner_ids=self.create_uid.partner_id.ids, body=mess_approve)
        else:
            raise UserError('người dùng chưa gửi yêu cầu duyệt')

    def btn_refuse(self):
        mess_refuse = 'Kế hoạch mới "%s" của bạn đã bị từ chối vào %s' % (self.sale_order_id.name,fields.Datetime.now())
        if self.sale_order_id.state == 'send':
            self.approve_status = 'refuse'
            # lấy ra all status của danh sách người phê duyệt
            states = self.sale_order_id.approve_id.mapped('approve_status')
            # chỉ cần có 1 người từ chối duyệt thì state = refuse và gửi thông báo
            if ([state == 'refuse'] for state in states):
                self.sale_order_id.state = 'refuse'
                self.sale_order_id.message_post(partner_ids=self.create_uid.partner_id.ids, body=mess_refuse)
        else:
            raise UserError('người dùng chưa gửi yêu cầu duyệt')

    # chỉ được duyệt hoặc từ chối duyệt cho approver mà mình được phân công
    def _compute_check_approve(self):
        # lấy ra all tên người phê duyệt trong danh sách người phê duyệt
        approvers = self.sale_order_id.approve_id.mapped('approver.name')
        for i in range(0, len(approvers)):
            # kiểm tra lần lượt approver trong database approver_list nếu trùng tên thì sẽ cho duyệt hoặc từ chối duyệt
            if approvers[i] == self.env.user.partner_id.name:
                self.sale_order_id.approve_id[i].check_approve = True
            else:
                self.sale_order_id.approve_id[i].check_approve = False
