# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    brand_id = fields.Many2one('product.brand', string='Marca', store=True, required=True)

    # printed = fields.Boolean()
    #
    # def do_print_picking(self):
    #     self.write({'printed': True})
    #     return self.env.ref('stock.action_report_picking').report_action(self)
