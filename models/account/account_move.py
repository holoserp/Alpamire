# -*- coding: utf-8 -*-

from odoo import models, api, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    def template_call(self):
        print(self)
        invoice = self.env["account.move"].search([('id', '=', self.id)])
        invoice_lines = invoice.invoice_line_ids.ids
        if invoice_lines:
            self.env.cr.execute("""
                    SELECT pt.name, pt.id, sum(aml.quantity) quantity, aml.price_unit, sum(aml.price_subtotal) subtotal
                    FROM account_move_line aml
                    LEFT JOIN product_product pp ON pp.id = aml.product_id
                    LEFT JOIN product_template pt ON pt.id = pp.product_tmpl_id
                    INNER JOIN account_move am ON am.id = aml.move_id
                    WHERE aml.move_id = am.id
                    AND pp.id = aml.product_id 
                    AND aml.id IN %s
                    GROUP BY pt.name, pt.id, aml.price_unit
            """, (tuple(invoice_lines),))
            lines_d = self.env.cr.dictfetchall()
            print(lines_d)
        else:
            lines_d = []
        return lines_d
