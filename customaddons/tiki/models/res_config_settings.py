from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    client_id = fields.Char(string='Client Id', config_parameter='client.id')
    client_secret = fields.Char(string='Client Secret', config_parameter='client.secret')
    url_tiki = fields.Char(string="Url Tiki", config_parameter='url.tiki')
    tiki_api = fields.Char(string="Tiki Api", config_parameter='tiki.api')

    def btn_connect_tiki(self):
        category = self.env['category.tiki'].get_categories_tiki
        warehouses = self.env['warehouses.tiki'].get_warehouses_tiki
