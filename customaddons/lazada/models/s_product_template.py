import lazop_sdk,json
import http.client
import logging
import json,requests
import jwt
import calendar
import time, hmac, hashlib

from odoo import fields, models

class SProductProduct(models.Model):
    _inherit = 'product.template'

    def create_product_lazada(self):
        appKey = self.env['ir.config_parameter'].sudo().get_param('app.key.lazada', '')
        secret = self.env['ir.config_parameter'].sudo().get_param('app.secret.lazada', '')
        # api = "/category/brands/query"
        token = self.env['base.integrate.lazada'].get_token_tiki()
        lazada_url = self.env['ir.config_parameter'].sudo().get_param('lazada.url', '')
        client = lazop_sdk.LazopClient(lazada_url, appKey, secret)
        request = lazop_sdk.LazopRequest('/product/create')
        request.add_api_param('payload',
                              '{     \"Request\": {         \"Product\": {             \"PrimaryCategory\": \"10002019\",             \"Images\": {                 \"Image\": [                     \"XXX\"                 ]             },             \"Attributes\": {                 \"name\": \"test 2022 02\",                 \"description\": \"TEST\",                 \"brand\": \"No Brand\",                 \"model\": \"test\",                 \"waterproof\": \"Waterproof\",                 \"warranty_type\": \"Local seller warranty\",                 \"warranty\": \"1 Month\",                 \"short_description\": \"cm x 1efgtecm<br /><brfwefgtek\",                 \"Hazmat\": \"None\",                 \"material\": \"Leather\",                 \"laptop_size\": \"11 - 12 inches\",                 \"delivery_option_sof\": \"No\"             },             \"Skus\": {                 \"Sku\": [                     {                         \"SellerSku\": \"test2022 02\",                         \"quantity\": \"3\",                         \"price\": \"35\",                         \"special_price\": \"33\",                         \"special_from_date\": \"2022-06-20 17:18:31\",                         \"special_to_date\": \"2025-03-15 17:18:31\",                         \"package_height\": \"10\",                         \"package_length\": \"10\",                         \"package_width\": \"10\",                         \"package_weight\": \"0.5\",                         \"package_content\": \"laptop bag\",                         \"Images\": {                             \"Image\": [                                 \"XXX\"                             ]                         }                     }                 ]             }         }     } }')
        response = client.execute(request, token)
        print(response.type)
        print(response.body)

