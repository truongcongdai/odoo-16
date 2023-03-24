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
    status = fields.Boolean("Status")
    street = fields.Text("Street")
    country_name = fields.Char("Country Name")
    country_code = fields.Char("Country Code")
    region_name = fields.Char("Region Name")
    region_code = fields.Char("Region Code")
    district_name = fields.Char("District Name")
    district_code = fields.Char("District Code")
    ward_name = fields.Char("Ward Name")
    ward_code = fields.Char("Ward Code")


    def get_warehouses_seller_tiki(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2/sellers/me/warehouses" % url_tiki
        req = self.env['base.integrate.tiki']._get_data_tiki(url=url, token=token)
        if req.status_code == 200:
            self.env['warehouses.seller.tiki'].sudo().search([]).unlink()
            for res in req.json()['data']:
                self.env['warehouses.seller.tiki'].sudo().create({
                    'name': res['name'],
                    'warehouses_id_seller': res['id'],
                    'is_primary': res['is_primary'],
                    'street': res['street'],
                    'country_name': res['country']['name'],
                    'country_code': res['country']['code'],
                    'district_name': res['district']['name'],
                    'district_code': res['district']['code'],
                    'ward_name': res['ward']['name'],
                    'ward_code': res['ward']['code'],
                    'status': res['status']
                })
            print('oke')