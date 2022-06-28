# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_create_batch(self):
        PickingIds = []
        PackingIds = []
        for rec in self:
            picking = rec.picking_ids.filtered(lambda p: p.picking_type_id.id == 3)
            PickingIds.append(picking)
            packing = rec.picking_ids.filtered(lambda p: p.picking_type_id.id == 4)
            PackingIds.append(packing)
        batch_picking = self.env['stock.picking.batch'].create({
            'company_id': self.env.company.id,
            'user_id': self.user_id.id,
            'picking_type_id': PickingIds[0].picking_type_id.id,
            'picking_ids': [(4, pick.id) for pick in PickingIds],
        }).action_confirm()
        batch_packing = self.env['stock.picking.batch'].create({
            'company_id': self.env.company.id,
            'user_id': self.user_id.id,
            'picking_type_id': PackingIds[0].picking_type_id.id,
            'picking_ids': [(4, pack.id) for pack in PackingIds],
        }).action_confirm()
        # ToDO REV
        self.create_log_book()
        self.write({'state': 'printed'})
        return self.env.ref('sale.action_report_saleorder').report_action(self)

    batch_count = fields.Integer(string='Batch Count', compute='_compute_batch_ids')
    batch_ids = fields.One2many('stock.picking.batch', string='Batch Count', compute='_compute_batch_ids')

    @api.depends('picking_ids')
    def _compute_batch_ids(self):
        for order in self:
            order.batch_ids = self.env['stock.picking.batch'].search([('picking_ids', 'in', order.picking_ids.ids)])
            order.batch_count = len(order.batch_ids)

    def action_view_batch(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock_picking_batch.stock_picking_batch_action")
        batches = self.mapped('batch_ids')
        if len(batches) > 1:
            action['domain'] = [('id', 'in', batches.ids)]
        elif batches:
            form_view = [(self.env.ref('stock_picking_batch.stock_picking_batch_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = batches.id
        # Prepare the context.
        batch_id = batches
        if batch_id:
            batch_id = batch_id[0]
        else:
            batch_id = batches[0]
        action['context'] = dict(self._context)
        return action

    state = fields.Selection(selection_add=[('printed', 'Impreso')])
    log_book = fields.Char(string='Log Book', copy=False)

    def create_log_book(self):
        self.log_book = self.env['ir.sequence'].next_by_code('sale.order.log.book')

    def action_print_sale_order_to_delivery(self):
        if self.filtered(lambda so: so.state != 'done'):
            raise UserError(_('Only done orders can be printed directly.'))
        self.create_log_book()
        self.write({'state': 'printed'})
        return self.env.ref('sale.action_report_saleorder').report_action(self)

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
