from odoo import fields, models,api

class WarehousesTiki(models.Model):
    _name = 'warehouses.tiki'
    name = fields.Char(string='Tên category')
    code = fields.Char(string='Code')
    qtyAvailable = fields.Integer(string='Số lượng tồn kho')
    warehouses_id = fields.Char(string="Warehouses Id")
    product_warehouses = fields.Many2one('product.template', string='Product')

    def get_warehouses_tiki(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        tiki_api = self.env['ir.config_parameter'].sudo().get_param('tiki.api', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2/warehouses/tiki" % url_tiki
        req = self.env['base.integrate.tiki']._get_data_tiki(url=url, token=token)
        if req.status_code == 200:
            self.env['warehouses.tiki'].sudo().search([]).unlink()
            for res in req.json():
                self.env['warehouses.tiki'].sudo().create({
                    'name': res['name'],
                    'code': res['code'],
                    'warehouses_id': res['id']
                })

class  WerehousesTikiLine(models.Model):
    _name ="warehouses.tiki.line"

    attribute_id = fields.Many2one('warehouses.tiki', string='Kho')
    attribute_seller_id = fields.Many2one('warehouses.seller.tiki', string='Kho')
    qtyAvailable = fields.Integer('Số lượng trong kho')
    product_id_warehouses = fields.Many2one('product.product',string='Product')

class  WarehousesSeller(models.Model):
    _name ="warehouses.seller.tiki"

    name = fields.Char(string='Tên warehouses seller')
    warehouses_id_seller = fields.Char(string="Warehouses Id")
    is_primary = fields.Boolean()
    seller_id = fields.Char()
    status = fields.Boolean()


    def get_warehouses_seller_tiki(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        tiki_api = self.env['ir.config_parameter'].sudo().get_param('tiki.api', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2/seller-inventories?tiki_warehouse_codes=" % url_tiki
        req = self.env['base.integrate.tiki']._get_data_tiki(url=url, token=token)
        if req.status_code == 200:
            self.env['warehouses.seller.tiki'].sudo().search([]).unlink()
            for res in req.json()['seller_inventories']:
                self.env['warehouses.seller.tiki'].sudo().create({
                    'name': res['name'],
                    'warehouses_id_seller': res['id'],
                    'is_primary': res['is_primary'],
                    'seller_id': res['seller_id'],
                    'status': res['status']
                })
