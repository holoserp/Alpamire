# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    pick_ids_lines = fields.One2many('stock.move.line', string='Pick Lines', compute='_compute_pick_ids_lines')

    @api.depends('pick_ids')
    def _compute_pick_ids_lines(self):
        for res in self:
            pick_ids_lines = res.pick_ids.move_line_ids_without_package.filtered(lambda l: l.qty_done != l.product_uom_qty)
            res.pick_ids_lines = [(6, 0, [x.id for x in pick_ids_lines])]
