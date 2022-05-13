# -*- coding: utf-8 -*-

from odoo import models, api, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    item = fields.Char('Item', compute='_compute_item', inverse='_set_item', search='_search_item')

    @api.depends('product_variant_ids.item')
    def _compute_item(self):
        self.item = False
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.item = template.product_variant_ids.item

    def _set_item(self):
        if len(self.product_variant_ids) == 1:
            self.product_variant_ids.item = self.item

    def _search_item(self, operator, value):
        templates = self.with_context(active_test=False).search([('product_variant_ids.item', operator, value)])
        return [('id', 'in', templates.ids)]
