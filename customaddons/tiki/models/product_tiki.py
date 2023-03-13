from odoo import fields, api, models
from odoo.exceptions import ValidationError, UserError
import json
import http.client

class ProductTiki(models.Model):
    _inherit = 'product.product'
    name = fields.Char(string="Tên sản phẩm")
    attribute_id = fields.One2many('product.attribute', 'product_id')
    brand_id = fields.Many2one('brand.tiki', string='Thương hiệu')
    product_category_id = fields.Many2one('category.tiki', string="Danh mục sản phẩm")
    origin = fields.Many2one('product.origin', string="Xuất xứ (Quốc gia)")
    brand_country = fields.Many2one('product.origin', string="Xuất xứ thương hiệu (Quốc gia)")
    description = fields.Char('Mô tả')
    product_height = fields.Float(string="Chiều cao")
    product_width = fields.Float(string="Chiều rộng")
    product_length = fields.Float(string="Chiều dài")
    product_weight_kg = fields.Float('Trọng lượng sau đóng gói (kg)')
    is_warranty_applied = fields.Selection([('0', 'Không có bảo hành'),
                                            ('1', 'Có bảo hành')
                                            ], default="0", string="Sản phẩm có bảo hành không?")
    inventory_type = fields.Selection([('dropship', 'FBT - Hàng lưu kho tiki'),
                                       ('instock', 'Nhà bán tự đóng gói, Tiki giao hàng'),
                                       ], string='Mô hình vận hành')
    warehouse_product_id = fields.One2many('warehouses.tiki.line', 'product_id_warehouses', string='Kho Tiki')
    image = fields.Image(string="Ảnh sản phẩm")
    is_auto_turn_on = fields.Boolean('Auto turn', default=False)
    ulr_image = fields.Text('Đường dẫn ảnh tài liệu')
    type_certificate = fields.Selection([('brand', 'Brand')], string="Type")
    price = fields.Float('Giá bán')
    sku = fields.Char(string='Mã sản phẩm')
    is_option = fields.Boolean('Có thêm lựa chọn sản phẩm?', default=False)
    track_id = fields.Char(string='Track ID')

    @api.onchange('product_weight_kg', 'product_length', 'product_width', 'product_height', 'product_height')
    def _onchange_info(self):
        if self.product_length < 0 or self.product_weight_kg < 0 or self.product_width < 0 or self.product_height < 0:
            raise ValidationError("Giá trị phải lớn hơn 0")

    def create_product_tiki(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')

        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2.1/requests"%url_tiki
        payload={
            "category_id": self.product_category_id.category_id,
            "name": self.name,
            "description": self.description,
            "attributes": {
                "bulky": 0,
                "brand": self.brand_id.name,
                "brand_country": self.brand_country.name,
                "origin": self.origin.name,
                "product_height": self.product_height,
                "product_width": self.product_width,
                "product_length": self.product_length,
                "product_weight_kg": self.product_weight_kg,
                "is_warranty_applied": self.is_warranty_applied
            },
            "image": "https://i1.sndcdn.com/artworks-Tiwyui2RowYzRxCL-IbJYXQ-t500x500.jpg",
            "option_attributes": [],
            "variants": [

            ],
            "certificate_files": [
                {
                    "url": self.ulr_image,
                    "type": self.type_certificate
                }
            ],
            "meta_data": {
                "is_auto_turn_on": self.is_auto_turn_on
            }
        }
        warehouse_stocks = []
        warehouse_id = self.warehouse_product_id.attribute_id.mapped('warehouses_id')
        qtyAvailable = self.warehouse_product_id.mapped('qtyAvailable')
        for warehouse_id, qtyAvailable in zip(warehouse_id, qtyAvailable):
            warehouse_stocks.append({
                "warehouse_id": warehouse_id,
                "qtyAvailable": qtyAvailable
            })
        # get atributes
        for r in self.attribute_id.mapped('name'):
            payload['option_attributes'].append(r)

        if len(payload['option_attributes']) == 0:
            payload['variants'].append({
                "sku": self.sku,
                "price": self.price,
                "option1": "none",
                "inventory_type": self.inventory_type,
                "warehouse_stocks": warehouse_stocks,
                "image": "https://images-na.ssl-images-amazon.com/images/I/715uwlmCWsLBY.jpg"
            })
        else:
            price = self.attribute_id.value_ids.mapped('price')
            sku = self.attribute_id.value_ids.mapped('sku')
            image = self.attribute_id.value_ids.mapped('image')
            name = self.attribute_id.value_ids.mapped('name')
            if len(payload['option_attributes']) == 1:
                for price, sku, image, name in zip(price, sku, image, name):
                    payload['variants'].append({
                        "sku": sku,
                        "option1": name,
                        "price": price,
                        "inventory_type": self.inventory_type,
                        "warehouse_stocks": warehouse_stocks,
                        "image": "https://images-na.ssl-images-amazon.com/images/I/715uwlmCWsLBY.jpg",
                    })
            if len(payload['option_attributes']) == 2:
                for r in range(len(self.attribute_id)):
                    attribute = {
                        "sku": self.attribute_id[r].value_ids[r].sku,
                        "option1": self.attribute_id[r].value_ids[0].name,
                        "option2": self.attribute_id[r].value_ids[1].name,
                        "price": self.attribute_id[r].value_ids[r].price,
                        "inventory_type": self.inventory_type,
                        "warehouse_stocks": warehouse_stocks,
                        "image": "https://images-na.ssl-images-amazon.com/images/I/715uwlmCWsLBY.jpg",
                    }
                    payload['variants'].append(attribute)
        res = self.env['base.integrate.tiki']._post_data_tiki(url=url, token=token, data=json.dumps(payload))
        if res.status_code == 200:
            self.track_id = res.json()['track_id']


    def get_product_unapproved(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2/requests" % url_tiki
        res = self.env['base.integrate.tiki']._get_data_tiki(url=url, token=token)


    def get_product_approved(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2/requests" %url_tiki
        res = self.env['base.integrate.tiki']._get_data_tiki(url=url, token=token)

    # def product_tracking_tiki(self):
    #     url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
    #     token = self.env['base.integrate.tiki'].get_token_tiki()
    #     # track_id = self.track_id
    #     url = "%s/integration/v2/tracking/%s"%(url_tiki,track_id)
    #     headers = {
    #         'tiki-api': '7a34ac38-a33e-4335-9e88-b80615ca624b',
    #         'Content-Type': 'application/json',
    #         "Authorization": "Bearer %s" % token
    #     }
    #     req = requests.get(
    #         url,
    #         headers=headers
    #     )

    # def delete_product_tiki(self):
    #     url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
    #     token = self.env['base.integrate.tiki'].get_token_tiki()
    #     url = "%s/integration/v2/requests/%s" %(url_tiki)
    #     headers = {
    #         'tiki-api': '7a34ac38-a33e-4335-9e88-b80615ca624b',
    #         'Content-Type': 'application/json',
    #         "Authorization": "Bearer %s" % token
    #     }
    #     req = requests.get(
    #         url,
    #         headers=headers
    #     )
