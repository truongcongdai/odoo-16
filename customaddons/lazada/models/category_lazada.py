import lazop_sdk

from odoo import fields, models,api
import requests
class CategoryLazada(models.Model):
    _name = 'category.lazada'

    category_id = fields.Integer(string="Category Id")
    name = fields.Char(string='Tên category', index='trigram')
    var = fields.Boolean()
    leaf = fields.Boolean()

    def get_categories_lazada(self):
        api = "/category/tree/get"
        lazada_url = self.env['ir.config_parameter'].sudo().get_param('lazada.url', '')
        token = self.env['base.integrate.lazada'].get_token_tiki()
        ts, sign = self.env['base.integrate.lazada'].get_sign_lazada(api, token)
        req = self.env['base.integrate.lazada']._get_data_lazada(lazada_url,api ,sign , ts,token)
        print(req)



