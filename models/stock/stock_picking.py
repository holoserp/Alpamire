# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_is_zero, float_round


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_barcode_view_state(self):
        """ Return the initial state of the barcode view as a dict.
        """
        if self.env.context.get('company_id'):
            company = self.env['res.company'].browse(self.env.context['company_id'])
        else:
            company = self.env.company
        picking_fields_to_read = self._get_picking_fields_to_read()
        move_line_ids_fields_to_read = self._get_move_line_ids_fields_to_read()
        pickings = self.read(picking_fields_to_read)
        source_location_list, destination_location_list = self._get_locations()
        for picking in pickings:
            picking['move_line_ids'] = self.env['stock.move.line'].browse(picking.pop('move_line_ids')).read(move_line_ids_fields_to_read)

            # Prefetch data
            product_ids = tuple(set([move_line_id['product_id'][0] for move_line_id in picking['move_line_ids']]))
            tracking_and_barcode_per_product_id = {}
            for res in self.env['product.product'].with_context(active_test=False).search_read([('id', 'in', product_ids)], ['tracking', 'item', 'barcode']):
                tracking_and_barcode_per_product_id[res.pop("id")] = res

            for move_line_id in picking['move_line_ids']:
                id = move_line_id.pop('product_id')[0]
                move_line_id['product_id'] = {"id": id, **tracking_and_barcode_per_product_id[id]}
                id, name = move_line_id.pop('location_id')
                move_line_id['location_id'] = {"id": id, "display_name": name}
                id, name = move_line_id.pop('location_dest_id')
                move_line_id['location_dest_id'] = {"id": id, "display_name": name}
            id, name = picking.pop('location_id')
            picking['location_id'] = self.env['stock.location'].with_context(active_test=False).search_read(
                [('id', '=', id)], ['parent_path']
            )[0]
            picking['location_id'].update({'display_name': name})
            id, name = picking.pop('location_dest_id')
            picking['location_dest_id'] = self.env['stock.location'].with_context(active_test=False).search_read(
                [('id', '=', id)], ['parent_path']
            )[0]
            picking['location_dest_id'].update({'display_name': name})
            picking['group_stock_multi_locations'] = self.env.user.has_group('stock.group_stock_multi_locations')
            picking['group_tracking_owner'] = self.env.user.has_group('stock.group_tracking_owner')
            picking['group_tracking_lot'] = self.env.user.has_group('stock.group_tracking_lot')
            if picking['group_tracking_lot']:
                picking['usable_packages'] = self.env['stock.quant.package'].get_usable_packages_by_barcode()
            picking['group_production_lot'] = self.env.user.has_group('stock.group_production_lot')
            picking['group_uom'] = self.env.user.has_group('uom.group_uom')
            picking['use_create_lots'] = self.env['stock.picking.type'].browse(picking['picking_type_id'][0]).use_create_lots
            picking['use_existing_lots'] = self.env['stock.picking.type'].browse(picking['picking_type_id'][0]).use_existing_lots
            picking['show_entire_packs'] = self.env['stock.picking.type'].browse(picking['picking_type_id'][0]).show_entire_packs
            picking['actionReportDeliverySlipId'] = self.env.ref('stock.action_report_delivery').id
            picking['actionReportBarcodesZplId'] = self.env.ref('stock.action_label_transfer_template_zpl').id
            picking['actionReportBarcodesPdfId'] = self.env.ref('stock.action_label_transfer_template_pdf').id
            picking['actionReturn'] = self.env.ref('stock.act_stock_return_picking').id
            if self.env.company.nomenclature_id:
                picking['nomenclature_id'] = [self.env.company.nomenclature_id.id]
            picking['source_location_list'] = source_location_list
            picking['destination_location_list'] = destination_location_list
        return pickings

    # ToDo REV put in pack for sequence per SaleOrder maybe add new modelo sale.order.package to set sequence
    # def _put_in_pack(self, move_line_ids, create_package_level=True):
    #     package = False
    #     for pick in self:
    #         move_lines_to_pack = self.env['stock.move.line']
    #         package = self.env['stock.quant.package'].create({})
    #         sequence = self.env['sale.order'].search([('name', '=', pick.origin)]).name
    #         package.write({"name": sequence})
    #
    #         precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #         if float_is_zero(move_line_ids[0].qty_done, precision_digits=precision_digits):
    #             for line in move_line_ids:
    #                 line.qty_done = line.product_uom_qty
    #
    #         for ml in move_line_ids:
    #             if float_compare(ml.qty_done, ml.product_uom_qty,
    #                              precision_rounding=ml.product_uom_id.rounding) >= 0:
    #                 move_lines_to_pack |= ml
    #             else:
    #                 quantity_left_todo = float_round(
    #                     ml.product_uom_qty - ml.qty_done,
    #                     precision_rounding=ml.product_uom_id.rounding,
    #                     rounding_method='UP')
    #                 done_to_keep = ml.qty_done
    #                 new_move_line = ml.copy(
    #                     default={'product_uom_qty': 0, 'qty_done': ml.qty_done})
    #                 vals = {'product_uom_qty': quantity_left_todo, 'qty_done': 0.0}
    #                 if pick.picking_type_id.code == 'incoming':
    #                     if ml.lot_id:
    #                         vals['lot_id'] = False
    #                     if ml.lot_name:
    #                         vals['lot_name'] = False
    #                 ml.write(vals)
    #                 new_move_line.write({'product_uom_qty': done_to_keep})
    #                 move_lines_to_pack |= new_move_line
    #         if create_package_level:
    #             package_level = self.env['stock.package_level'].create({
    #                 'package_id': package.id,
    #                 'picking_id': pick.id,
    #                 'location_id': False,
    #                 'location_dest_id': move_line_ids.mapped('location_dest_id').id,
    #                 'move_line_ids': [(6, 0, move_lines_to_pack.ids)],
    #                 'company_id': pick.company_id.id,
    #             })
    #         move_lines_to_pack.write({
    #             'result_package_id': package.id,
    #         })
    #     return package
