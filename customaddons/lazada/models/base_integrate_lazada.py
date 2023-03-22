import base64

import lazop_sdk

from odoo import models, fields
import http.client
import logging
import json,requests
import jwt
import calendar
import time, hmac, hashlib
from rauth import OAuth2Service

class BaseIntegrateLazada(models.Model):
    _name = 'base.integrate.lazada'

    token = fields.Char(string="Token")

    def get_token_tiki(self):
        appKey = self.env['ir.config_parameter'].sudo().get_param('app.key.lazada', '')
        appSecret = self.env['ir.config_parameter'].sudo().get_param('app.secret.lazada', '')
        authorizationCode = self.env['ir.config_parameter'].sudo().get_param('authorization.code', '')
        client = lazop_sdk.LazopClient("https://auth.lazada.com/rest", appKey, appSecret)
        request = lazop_sdk.LazopRequest("/auth/token/create")
        request.add_api_param("code", authorizationCode)

        response = client.execute(request)
        check = response.code
        if check == '0':
            self.env['base.integrate.lazada'].sudo().search([]).unlink()
            self.env['base.integrate.lazada'].sudo().create({
                'token': response.body['access_token']
            })
            access_token = response.body['access_token']
        else:
            access_token = self.sudo().search([]).token
        return access_token

    def get_sign_lazada(self,api,token):
        app_secret = self.env['ir.config_parameter'].sudo().get_param('app.secret.lazada', '')
        # timestamp in milliseconds
        timestamp = int(time.time() * 1000.0)
        app_key = self.env['ir.config_parameter'].sudo().get_param('app.key.lazada', '')
        parameters = {
            "app_key": app_key,
            "timestamp": timestamp,
            "sign_method": "sha256",
            "access_token": token
        }
        sort_dict = sorted(parameters)
        parameters_str = "%s%s" % (api, str().join('%s%s' % (key, parameters[key]) for key in sort_dict))
        h = hmac.new(app_secret.encode(encoding="utf-8"), parameters_str.encode(encoding="utf-8"), digestmod=hashlib.sha256)
        return str(timestamp),h.hexdigest().upper()

    def _get_data_lazada(self, url,api ,sign , ts,token, data=None, files=None, params=None, headers=None):
        app_key = self.env['ir.config_parameter'].sudo().get_param('app.key.lazada', '')
        url = url + api + '?app_key=' + app_key + '&timestamp=' + ts + '&access_token=' + token + '&sign_method=sha256&sign=' + sign
        req = requests.get(url).json()
        return req

    # def _post_data_tiki(self, url, token, data=None, files=None, params={}, headers=None):
    #     tiki_api = self.env['ir.config_parameter'].sudo().get_param('tiki.api', '')
    #     if headers is None:
    #         headers = {
    #             'tiki-api': tiki_api,
    #             'Content-Type': 'application/json',
    #             'Authorization': 'Bearer %s' % (token,),
    #             'User-Agent': 'Odoo'
    #         }
    #     data = data or dict()
    #     res = requests.post(
    #         url,
    #         data=data,
    #         params=params,
    #         files=files,
    #         headers=headers,
    #         verify=False
    #     )
    #     return res




