# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ProductBrand(models.Model):
    _inherit = 'product.brand'

    user_ids = fields.Many2many('res.users', 'product_brand_users_rel', 'product_brand_id', 'user_id',
                                'Usuarios Permitidos')
