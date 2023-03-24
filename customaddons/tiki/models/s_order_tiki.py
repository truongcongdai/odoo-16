from odoo import fields, api, models
import http.client
import json


class OrderTiki(models.Model):
    _inherit = "sale.order"

    id_order = fields.Char(string="Mã đơn hàng")
    fulfillment_type = fields.Selection([('tiki_delivery', "Tiki Vận chuyển"),
                                         ('seller_dilivery', "Người bán giao hàng"),
                                         ('cross_border', "Giao từ nước ngoài"),
                                         ('dropship', "Tiki giao hàng"),
                                         ('instant_delivery', "Giao hàng nhanh")], string="Hình thức giao hàng")
    status = fields.Selection([('cho_in', "Chờ xác nhận"),
                               ("canceled", "Đơn hàng bị hủy"),
                               ("giao_hang_thanh_cong", "Giao hàng thành công"),
                               ("complete", "Đơn hàng hoàn thành")], default='cho_in', string="Trạng thái")
    is_rma = fields.Boolean("Có phải là đơn hàng thay thế không?")
    is_vat_exporting = fields.Boolean("Có xuất hóa đơn VAT không?")
    warehouse_ids = fields.Many2one("warehouses.tiki", string="Kho hàng tiki")
    method = fields.Selection([("cod", "Thanh toán tiền mặt"),
                               ("cybersource", "Thanh toán bằng nguồn tiền")], string="Phương thức thanh toán")

    seller_warehouse = fields.Many2one('warehouses.seller.tiki', string="Kho người bán")
    seller_inventory_id = fields.Char('Id kho hàng tồn')
    partner_name = fields.Many2one('res.partner', string="Đối tác vận chuyển")
    partner_shipping_id = fields.Many2one('res.partner', string="Địa chỉ giao hàng")
    shipping_status = fields.Selection([('New', "Giao hàng"),
                                        ('Delivered', 'Đã giao hàng')
                                        ], string="Trạng thái giao hàng")
    description_shipping = fields.Char("Kế hoạch giao hàng")

    def action_confirm(self):
            return super(OrderTiki, self).action_confirm()
    def action_cancel(self):
        return super(OrderTiki, self).action_cancel()
    def get_list_order(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2/orders" % url_tiki

        res = self.env['base.integrate.tiki']._get_data_tiki(url=url, token=token)
        if res.status == 200:
            res_json = res.json()
            # Trạng thái đơn hàng
            res_json['status'] = self.status
            # Thông tin kho
            warehousestiki_id = self.env['warehouses.tiki'].search(
                [('warehouses_id', '=', res_json['tiki_warehouse']['id'])]).id
            self.warehouse_ids = warehousestiki_id
            warehousesseller_id = self.env['warehouses.seller.tiki'].search(
                [('warehouses_id', '=', res_json['seller_warehouse']['id'])]).id
            self.seller_warehouse = warehousesseller_id

            self.seller_inventory_id = res_json['inventory_requisition']['seller_inventory_id']

#             Ngày giao hàng
            self.commitment_date = res_json['shipping']['plan']['promised_delivery_date']


class TikiIntegrationOrder(models.Model):
    _name = "tiki.integration.order"

    def _confirm_enough_stock_drop_shipping(self, payload, id):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2/orders/" + id + "/confirm-available" % url_tiki

        res = self.env['base.integrate.tiki']._post_data_tiki(url=url, token=token)
