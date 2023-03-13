from odoo import fields, models,api
import requests
class CategoryTiki(models.Model):
    _name = 'category.tiki'
    # _parent_name = "parent_id"
    # _parent_store = True
    # _rec_name = 'complete_name'

    category_id = fields.Integer(string="Category Id")
    name = fields.Char(string='Tên category', index='trigram')
    description = fields.Char(string='Mô tả')
    is_primary = fields.Boolean()
    is_product_listing_enabled = fields.Boolean()
    no_license_seller_enabled = fields.Boolean()

    category_product_id = fields.One2many('product.product','product_category_id')
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    parent_id_category = fields.Many2one('category.tiki', 'Parent Category', index=True, ondelete='cascade')
    parent_path = fields.Char(index=True, unaccent=False)
    child_id = fields.One2many('category.tiki', 'parent_id_category', 'Child Categories')


    def get_categories_tiki(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2/categories" % url_tiki
        req = self.env['base.integrate.tiki']._get_data_tiki(url=url, token=token)
        if req.status_code == 200:
            self.env['category.tiki'].sudo().search([]).unlink()
            self.env['category.tiki'].sudo().create({
                'name': "Tiki",
                'is_primary': True,
                'is_product_listing_enabled': True,
                'no_license_seller_enabled': True,
                'category_id': 1,
            })
            for res in req.json()['data']:
                self.env['category.tiki'].sudo().create({
                    'name': res['name'],
                    # 'parent_id_category':self.search([('category_id','=',res['parent_id'])]).id,
                    'is_primary': res['is_primary'],
                    # 'complete_name':'%s / %s' % (self.search([('category_id','=',res['parent_id'])]).name, res['name']),
                    'is_product_listing_enabled': res['is_product_listing_enabled'],
                    'no_license_seller_enabled': res['no_license_seller_enabled'],
                    'category_id': res['id']
                })
