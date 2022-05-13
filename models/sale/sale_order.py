# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

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
