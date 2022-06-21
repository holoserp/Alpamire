
from odoo import api, fields, models


class SaleOrderTypology(models.Model):
    _inherit = "sale.order.type"

    user_id = fields.Many2one('res.users', string='Vendedor')
