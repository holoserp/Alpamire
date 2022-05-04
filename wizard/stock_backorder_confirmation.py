# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    backorder_lines = fields.Many2many('stock.move.line', 'stock_move_line_backorder_lines_rel',
                                       compute='_compute_backorder_lines')

    # Todo FIXME for calculate lines in zero qty
    def _compute_backorder_lines(self):
        for pick in self.pick_ids.ids:
            for line in pick:
                self.backorder_lines += line
