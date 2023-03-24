import requests
from odoo import fields, api, models
from odoo.exceptions import ValidationError
import json


class SProductTemplate(models.Model):
    _inherit = 'product.template'
    name = fields.Char(string="Tên sản phẩm")
    attribute_id = fields.One2many('product.attribute', 'product_id')
    warehouse_product_id = fields.One2many('warehouses.tiki.line', 'product_id_warehouses', string='Kho Tiki')
    brand_id = fields.Many2one('brand.tiki', string='Thương hiệu',required=True)
    product_category_id = fields.Many2one('category.tiki', string="Danh mục sản phẩm",required=True)
    origin = fields.Many2one('product.origin', string="Xuất xứ (Quốc gia)",required=True)
    brand_country = fields.Many2one('product.origin', string="Xuất xứ thương hiệu (Quốc gia)",required=True)
    description = fields.Char('Mô tả',required=True)
    product_height = fields.Float(string="Chiều cao",default="0",required=True)
    product_width = fields.Float(string="Chiều rộng",default="0",required=True)
    product_length = fields.Float(string="Chiều dài",default="0",required=True)
    product_weight_kg = fields.Float('Trọng lượng sau đóng gói (kg)',default="0",required=True)
    # is_warranty_applied = fields.Selection([('0', 'Không có bảo hành'),
    #                                         ('1', 'Có bảo hành')
    #                                         ], default="0", string="Sản phẩm có bảo hành không?")
    inventory_type = fields.Selection([('dropship', 'Nhà bán tự đóng gói, Tiki giao hàng'),
                                       ('instock', 'FBT - Hàng lưu kho tiki'),
                                       ], string='Mô hình vận hành',required=True)
    # warehouse_product_id = fields.One2many('warehouses.tiki.line', 'product_id_warehouses', string='Kho Tiki')
    is_auto_turn_on = fields.Boolean('Auto turn', default=False)
    ulr_image = fields.Text('Tài liệu thương hiệu')
    type_certificate = fields.Selection([('brand', 'Brand')],default="brand" ,string="Type")
    sku = fields.Char(string='Sku')
    bulky = fields.Selection([("0", 'Không'),("1", 'Có'),], string='Hàng cồng kềnh',default="0")
    is_option = fields.Boolean(compute="check_is_option")
    track_id = fields.Char(string='Track ID')
    reason = fields.Html(string="Lý do Tiki",readonly="1")
    is_reason = fields.Boolean(default=False)
    request_id = fields.Char()
    state = fields.Selection([('none', 'New'),
                              ('processing', "Processing"),
                              ('drafted', 'Drafted'),
                              ('bot_awaiting_approve', "Bot Awaiting Approve"),
                              ('md_awaiting_approve', 'MD Awaiting Approve'),
                              ('awaiting_approve', 'Awaiting Approve'),
                              ('approved', 'Approved'),
                              ('rejected', 'Rejected'),
                              ('deleted', 'Deleted')
                              ], compute="state_product_tiki",string="Trạng thái tiki",default='none')
    tmpl_product_id = fields.One2many('product.product','product_tmpl_id')
    is_inventory_type = fields.Boolean(compute="_compute_is_inventory_type",default=False)
    is_brand_id = fields.Boolean(compute="_compute_is_brand_id",default=False)

    @api.depends('brand_id.name')
    def _compute_is_brand_id(self):
        self.is_brand_id = False
        if self.brand_id.name == 'OEM':
            self.is_brand_id = True

    def _compute_is_inventory_type(self):
        self.is_inventory_type = False
        if len(self.attribute_line_ids) >0:
            self.is_inventory_type = True

    @api.constrains('product_height','product_width','product_length','product_weight_kg')
    def constrains_weight_or_dimensions(self):
        for r in self:
            dimensions = round((r.product_height * r.product_width * r.product_length)/6000,2)
            if r.product_weight_kg < dimensions:
                if 0.001 > dimensions or dimensions > 100:
                    raise ValidationError("Trọng lượng vận chuyển nằm ngoài khoảng cho phép (0.001 ~ 100.0kg). Bạn hãy kiểm tra và điều chỉnh lại trọng lượng - kích thước sản phẩm")
            else:
                if 0.001 > r.product_weight_kg or r.product_weight_kg> 100:
                    raise ValidationError("Trọng lượng vận chuyển nằm ngoài khoảng cho phép (0.001 ~ 100.0kg). Bạn hãy kiểm tra và điều chỉnh lại trọng lượng - kích thước sản phẩm")

    @api.constrains('list_price')
    def constrains_price(self):
        for r in self:
            if not r.is_option and (r.list_price > 20000000 or r.list_price < 1000):
                raise ValidationError("Giá bán nằm ngoài khoảng cho phép (1000 ~ 20000000)VND. Bạn hãy kiểm tra và điều chỉnh lại giá bán sản phẩm")

    @api.constrains('sku')
    def check_sku(self):
        sku_template_attribute_count = self.env['product.product'].search_count([('sku', '=', self.sku)])
        sku_template_count = self.search_count([('sku', '=', self.sku)])
        count_sku = sku_template_attribute_count + sku_template_count
        if count_sku > 1:
            raise ValidationError('Sku đã được dùng. Vui lòng đổi Sku khác')

    def check_is_option(self):
        if self.attribute_line_ids:
            self.is_option = True
        else:
            self.is_option = False

    @api.onchange('attribute_line_ids')
    def _check_attribute_id(self):
        if len(self.attribute_line_ids.attribute_id) > 2:
            raise ValidationError("Not more than 2 attribute")

    @api.onchange('product_weight_kg', 'product_length', 'product_width', 'product_height', 'product_height')
    def _onchange_info(self):
        if self.product_length < 0 or self.product_weight_kg < 0 or self.product_width < 0 or self.product_height < 0:
            raise ValidationError("Giá trị phải lớn hơn 0")

    def create_product_tiki(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        url = "%s/integration/v2.1/requests"%url_tiki
        url_imgbb = "https://api.imgbb.com/1/upload"
        data = {
            "expiration":"300",
            "key": "abec198575d0126e6305462fcedb028a",
            "image": self.image_1920,
        }
        rec_image = requests.post(url_imgbb, data).json()
        https_image = rec_image['data']['url']
        payload={
            "category_id": self.product_category_id.category_id,
            "name": self.name,
            "description": self.description,
            "attributes": {
                "bulky": int(self.bulky),
                "brand": self.brand_id.name,
                "brand_country": self.brand_country.name,
                "origin": self.origin.name,
                "product_height": self.product_height,
                "product_width": self.product_width,
                "product_length": self.product_length,
                "product_weight_kg": self.product_weight_kg,
                "is_warranty_applied": 0
            },
            "image": https_image,
            "option_attributes": [],
            "variants": [],
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
        if self.is_option:
            payload["option_attributes"].extend(self.attribute_line_ids.attribute_id.mapped('name'))
        if len(payload['option_attributes']) == 0:
            payload['variants'].append({
                "sku": self.sku,
                "price": self.list_price,
                "option1": "none",
                "inventory_type": self.inventory_type,
                "seller_warehouse":"",
                "warehouse_stocks": [],
            })
            if self.warehouse_product_id and self.inventory_type == 'dropship':
                for i in range(len(self.warehouse_product_id)):
                    payload['variants'][0]['warehouse_stocks'].append({
                        "warehouseId": self.warehouse_product_id[i].attribute_seller_id.warehouses_id_seller,
                        "qtyAvailable": self.warehouse_product_id[i].qtyAvailable
                    })
                    payload['variants'][0]['seller_warehouse'] += self.warehouse_product_id[i].attribute_seller_id.warehouses_id_seller +","
                payload['variants'][0]['seller_warehouse'] = payload['variants'][0]['seller_warehouse'].rstrip(',')
        else:
            for r in range(len(self.product_variant_ids)):
                try:
                    data = {
                        "expiration": "300",
                        "key": "abec198575d0126e6305462fcedb028a",
                        "image": self.product_variant_ids[r].image_1920,
                    }
                    rec_image_variants = requests.post(url_imgbb, data).json()
                    https_image_variants = rec_image_variants['data']['url']
                except:
                    https_image_variants = ""
                payload['variants'].append({
                    "sku": self.product_variant_ids[r].sku,
                    "price": self.product_variant_ids[r].lst_price,
                    "inventory_type": self.inventory_type,
                    "seller_warehouse":"",
                    "warehouse_stocks": [],
                    "image": https_image_variants,
                })
                if self.product_variant_ids[r].warehouse_product_id and self.inventory_type == 'dropship':
                    for i in range(len(self.product_variant_ids[r].warehouse_product_id)):
                        payload['variants'][r]['warehouse_stocks'].append({
                            "warehouseId": self.product_variant_ids[r].warehouse_product_id[i].attribute_seller_id.warehouses_id_seller,
                            "qtyAvailable": self.product_variant_ids[r].warehouse_product_id[i].qtyAvailable
                        })
                        payload['variants'][r]['seller_warehouse'] += self.product_variant_ids[r].warehouse_product_id[i].attribute_seller_id.warehouses_id_seller + ","
                    payload['variants'][r]['seller_warehouse'] = payload['variants'][0]['seller_warehouse'].rstrip(',')

                if len(payload['option_attributes']) == 1:
                    payload['variants'][r].update({
                        "option1": self.product_variant_ids[r].product_template_variant_value_ids.name
                    })
                elif self.attribute_line_ids[0].value_count == 1:
                    payload['variants'][r].update({
                        "option1": self.attribute_line_ids[0].value_ids.name,
                        "option2":self.product_variant_ids[r].product_template_variant_value_ids.name,
                    })
                elif self.attribute_line_ids[1].value_count == 1:
                    payload['variants'][r].update({
                        "option1":self.product_variant_ids[r].product_template_variant_value_ids.name,
                        "option2": self.attribute_line_ids[1].value_ids.name,
                    })
                else:
                    payload['variants'][r].update({
                        "option1": self.product_variant_ids[r].product_template_variant_value_ids[0].name,
                        "option2": self.product_variant_ids[r].product_template_variant_value_ids[1].name,
                    })
        res = self.env['base.integrate.tiki']._post_data_tiki(url=url, token=token, data=json.dumps(payload))
        if res.status_code == 200:
            self.track_id = res.json()['track_id']

    def state_product_tiki(self):
        url_tiki = self.env['ir.config_parameter'].sudo().get_param('url.tiki', '')
        token = self.env['base.integrate.tiki'].get_token_tiki()
        track_id = self.track_id
        url = "%s/integration/v2/tracking/%s"%(url_tiki,track_id)
        if self.track_id:
            req = self.env['base.integrate.tiki']._get_data_tiki(url=url, token=token)
            if req.status_code == 200:
                self.state = req.json()['state']
                if req.json()['reason']:
                    self.is_reason = True
                    self.reason = req.json()['reason']
                else:
                    self.is_reason = False
        else:
            self.state = 'none'
