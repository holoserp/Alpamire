# -*- coding: utf-8 -*-

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_checked = fields.Float('Cantidad Comprobada')
    qty_inner = fields.Float(related='product_id.inner', readonly=True)

    def is_multiple(self, num, multiple):
        return num % multiple == 0

    # @api.onchange('product_uom_qty', 'qty_inner')
    # def _onchange_product_id_check_inner(self):
    #     if self.product_id.type == 'product' and self.product_uom_qty > 1:
    #         for line in self:
    #             inner = line.qty_inner
    #             qty = line.product_uom_qty
    #             if line.is_multiple(qty, inner):
    #                 pass
    #             else:
    #                 message = _('La Cantidad %s del Producto %s no es multiplo del INNER %s.') % \
    #                           (line.product_uom_qty, line.product_id.name, line.qty_inner)
    #                 raise ValidationError(_(message))
