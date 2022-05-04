# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


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
