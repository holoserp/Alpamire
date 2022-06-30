# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class StockPickingBatch(models.Model):
    _inherit = "stock.picking.batch"

    package_ids = fields.Many2many('stock.quant.package', compute='_compute_picking_packages', string='Packages')

    # @api.depends('move_line_ids', 'move_line_ids.result_package_id')
    @api.depends('picking_ids.move_line_ids', 'picking_ids.move_line_ids.result_package_id')
    def _compute_picking_packages(self):
        for batch in self:
            for package in batch.picking_ids:
                packs = set()
                for move_line in package.move_line_ids:
                    if move_line.result_package_id:
                        packs.add(move_line.result_package_id.id)
                package.package_ids = list(packs)

    def action_see_picking_packages(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("stock.action_package_view")
        # packages = self.move_line_ids.mapped('result_package_id')
        packages = self.picking_ids.move_line_ids.mapped('result_package_id')
        action['domain'] = [('id', 'in', packages.ids)]
        action['context'] = {'picking_id': self.id}
        return action
