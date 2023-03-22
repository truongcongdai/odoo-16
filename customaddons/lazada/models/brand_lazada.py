import lazop_sdk

from odoo import fields, models,api
import requests
class BrandLazada(models.Model):
    _name = 'brand.lazada'

    name = fields.Char(string="Name")
    global_identifier = fields.Char(string="Global Identifier")
    name_en = fields.Char(string="Name en")
    brand_id = fields.Integer(string="Brand Id")

    def get_brand_by_page_lazada(self):
        appKey = self.env['ir.config_parameter'].sudo().get_param('app.key.lazada', '')
        secret = self.env['ir.config_parameter'].sudo().get_param('app.secret.lazada', '')
        # api = "/category/brands/query"
        lazada_url = self.env['ir.config_parameter'].sudo().get_param('lazada.url', '')
        # token = self.env['base.integrate.lazada'].get_token_tiki()
        # ts, sign = self.env['base.integrate.lazada'].get_sign_lazada(api, token)
        client = lazop_sdk.LazopClient(lazada_url, appKey, secret)
        request = lazop_sdk.LazopRequest('/category/brands/query')
        request.add_api_param('startRow', '0')
        request.add_api_param('pageSize', '20')
        response = client.execute(request)
        check = response.code
        if check =='0':
            self.env['brand.lazada'].sudo().search([]).unlink()
            for r in response.body['data']['module']:
                self.env['brand.lazada'].sudo().create({
                    'name': r['name'],
                    'global_identifier': r['global_identifier'],
                    'name_en': r['name_en'],
                    'brand_id': r['brand_id'],
                })