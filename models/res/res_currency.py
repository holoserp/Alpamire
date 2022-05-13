
import requests
import json
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def _send_api_banxico(self):
        token = 'c89b04000ffaa4d785d3426cebdcd5acd1a98099e72d33865fb879f80094d218'
        request_url = 'https://www.banxico.org.mx/SieAPIRest/service/v1/series/SF43718/datos/oportuno?token=%s' % token
        headers = {'Content-Type': 'application/json'}
        try:
            req = requests.get(request_url, headers=headers)
            content = req.json()
            date = content['bmx']['series'][0]['datos'][0]['fecha']
            fix = content['bmx']['series'][0]['datos'][0]['dato']
            message = 'El tipo de cambio del dia %s es %s' % (date, fix)
            print(message)
            pass
        except requests.HTTPError:
            raise UserError(_("Error!"))
