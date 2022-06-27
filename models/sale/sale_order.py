# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    related_sale_orders = fields.Char(string='Pedidos Relacionados', copy=False)

    @api.model
    def create(self, vals):
        need_invoice = vals.get('need_invoice')
        if not need_invoice:
            raise UserError(_('No se ha establecido si el Pedido de Venta Necesita Factura!'))
        return super().create(vals)

    carrier_tracking_ref = fields.Char(string='Tracking Reference', copy=False)

    delivery_progress = fields.Float(string="Progress", help="Progress from zero delivery (0%) to fully delivery(100%).")
    #                                  , compute='_get_delivery_progress')
    #
    # @api.depends('picking_ids')
    # def _get_delivery_progress(self):
    #     """Return the percentage of completeness of the delivery, between 0 and 100"""
    #     for sale in self:
    #         for pick in sale.picking_ids:
    #             delivery_progress = 0.0
    #             delivery = pick.filtered(lambda s: s.picking_type_id.sequence_code == 'OUT')
    #             if delivery.state == 'done':
    #                 delivery_progress += 33.00
    #             packing = pick.filtered(lambda s: s.picking_type_id.sequence_code == 'PACK')
    #             if packing.state == 'done':
    #                 delivery_progress += 33.0
    #             picking = pick.filtered(lambda s: s.picking_type_id.sequence_code == 'PICK')
    #             if picking.state == 'done':
    #                 delivery_progress += 33.33
    #             if picking or packing or delivery:
    #                 sale.delivery_progress = delivery_progress
    #             else:
    #                 sale.delivery_progress = 0.0

    company_group_id = fields.Many2one('res.partner', string='Grupo compañía', related='partner_id.company_group_id')

    need_invoice = fields.Selection([('no', 'No'), ('yes', 'Sí')], required=True, string='Necesita Factura?')

    brand_id = fields.Many2one('product.brand', string='Marca', store=True, required=True)

    amount_untaxed_checked = fields.Monetary(string='Untaxed Amount Checked', store=True, readonly=True,
                                             compute='_amount_all_checked')
    amount_tax_checked = fields.Monetary(string='Taxes Checked', store=True, readonly=True,
                                         compute='_amount_all_checked')
    amount_total_checked = fields.Monetary(string='Total Checked', store=True, readonly=True,
                                           compute='_amount_all_checked')

    @api.depends('order_line.qty_checked')
    def _amount_all_checked(self):
        for order in self:
            amount_untaxed_checked = amount_tax_checked = 0.0
            for line in order.order_line:
                amount_untaxed_checked += line.price_unit * line.qty_checked
                amount_tax_checked += ((line.price_unit * line.qty_checked) * 0.16)
            order.update({
                'amount_untaxed_checked': amount_untaxed_checked,
                'amount_tax_checked': amount_tax_checked,
                'amount_total_checked': amount_untaxed_checked + amount_tax_checked,
            })

    @api.model
    def _default_type_id(self):
        return self.env["sale.order.type"].search([("company_id", "in", [self.env.company.id, False]),
                                                   ("user_id", "=", [self.env.user.id, False])], limit=1)

    def action_confirm(self):
        for order in self:
            if order.type_id:
                sequence = order.type_id.sequence_id.next_by_id()
                order.write({"name": sequence})
        return super().action_confirm()

    def action_create_batch(self):
        self.ensure_one()
        print('Lugar')
        pickings = self.env['stock.picking'].search('origin', 'like', self.name)
        print('pickings', pickings)

            # company = pickings.company_id
            # batch = self.env['stock.picking.batch'].create({
            #     'user_id': self.user_id.id,
            #     'company_id': company.id,
            #     'picking_type_id': pickings[0].picking_type_id.id,
            # })
            # pickings.write({'batch_id': batch.id})

    # printed = fields.Boolean()
    #
    # def do_print_picking(self):
    #     self.write({'printed': True})
    #     return self.env.ref('stock.action_report_picking').report_action(self)
