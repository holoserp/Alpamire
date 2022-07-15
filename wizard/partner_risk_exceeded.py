
from odoo import _, fields, models


class PartnerRiskExceededWiz(models.TransientModel):
    _inherit = "partner.risk.exceeded.wiz"

    def request_authorization(self):
        self.ensure_one()
        origen = self.origin_reference
        activity = self.env['mail.activity.type'].search([('name', '=', 'Autorizar Pedido')])
        for sale in origen:
            activity_request_authorization_values = {
                'activity_type_id': activity.id,
                'res_id': sale.id,
                'res_model_id': self.env.ref('sale.model_sale_order').id,
                'date_deadline': sale.date_order,
                'user_id': activity.default_user_id.id,
                'note': 'Autorización de Pedido',
                'summary': 'AUTORIZACIÓN PEDIDO'
            }
            activity_request_authorization = self.env['mail.activity'].create(activity_request_authorization_values)
