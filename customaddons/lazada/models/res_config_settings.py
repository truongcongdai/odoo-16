import lazop_sdk,json
import http.client
import logging
import json,requests
import jwt
import calendar
import time, hmac, hashlib

from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    app_key_lazada = fields.Char(string='App Key', config_parameter='app.key.lazada')
    app_secret_lazada = fields.Char(string='App Secret', config_parameter='app.secret.lazada')
    authorizationCode = fields.Char(string="Authorization Code", config_parameter='authorization.code')
    lazada_url = fields.Char(string="Lazada url", config_parameter='lazada.url')

    def btn_connect_lazada(self):
        # category = self.env['category.tiki'].get_categories_tiki
        print("oke")
        # warehouses = self.env['warehouses.tiki'].get_warehouses_tiki
