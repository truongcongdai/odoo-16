import base64

from odoo import models, fields
import http.client
import logging
import json,requests
import jwt
import calendar
import time, hmac, hashlib
from rauth import OAuth2Service

class BaseIntegrateTiki(models.Model):
    _name = 'base.integrate.tiki'

    test = fields.Char(string="Test")

    def get_token_tiki(self):
        conn = http.client.HTTPSConnection("api.tiki.vn")
        payload = 'grant_type=client_credentials'
        client_id = self.env['ir.config_parameter'].sudo().get_param('client.id', '')
        client_secret = self.env['ir.config_parameter'].sudo().get_param('client.secret', '')
        auth = (client_id + ":" + client_secret).encode()
        authorization_byte = base64.b64encode(auth)
        authorization_string = authorization_byte.decode('ascii')
        headers = {
            'Authorization': 'Basic %s'%authorization_string,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        conn.request("POST", "/sc/oauth2/token", payload, headers)
        res = conn.getresponse()
        data = res.read()
        return json.loads(data.decode("utf-8"))['access_token']

    def _post_data_tiki(self, url, token, data=None, files=None, params={}, headers=None):
        tiki_api = self.env['ir.config_parameter'].sudo().get_param('tiki.api', '')
        if headers is None:
            headers = {
                'tiki-api': tiki_api,
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % (token,),
                'User-Agent': 'Odoo'
            }
        data = data or dict()
        res = requests.post(
            url,
            data=data,
            params=params,
            files=files,
            headers=headers,
            verify=False
        )
        return res
    def _get_data_tiki(self, url, token, data=None, files=None, params=None, headers=None):
        if headers is None:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % (token,),
                'User-Agent': 'Odoo'
            }
        data = data or dict()
        res = requests.get(
            url,
            data=data,
            params=params,
            files=files,
            headers=headers,
            verify=False
        )
        return res



