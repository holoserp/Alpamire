# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import all_timezones, timezone
from odoo import api, fields, models, tools
from odoo.addons.base.models.res_partner import _tzs
from odoo.addons.resource.models.resource import datetime_to_string, Intervals, string_to_datetime
from odoo.tools.safe_eval import safe_eval

def get_possible_timezones_by_offset(tz_offset):
    """
    The method to retrieve a possible timezone by its offset (we return the first found)

    Args:
     * tz_offset - int (offset in minutes)

    Returns:
     * char
    """
    offset_days, offset_seconds = 0, int(tz_offset * 60)
    if offset_seconds < 0:
        offset_days = -1
        offset_seconds += 24 * 60
    desired_delta = timedelta(offset_days, offset_seconds)
    null_delta = timedelta(0, 0)
    result = "UTC"
    for tz_name in all_timezones:
        tz = timezone(tz_name)
        non_dst_offset = getattr(tz, '_transition_info', [[null_delta]])[-1]
        if desired_delta == non_dst_offset[0]:
            result = tz_name
            break
    return result


class BusinessResource(models.Model):
    _inherit = 'business.resource'

    @api.model
    def _find_tz_options(self, tz_info):
        """
        The method to return timezone option
         1. If receive target_tz we use it
            [It also means that the option of tz is turned on (since selection is shown) --> we do not need to check
            configuration]
         2. Otherwise we just take tz received from js
         3. In case default timezone received from JS is not among pytz timezones (an extreme option)--> get try to get
            any with the same offset
         4. If selection is not assumed at all we pass an empty list and as default tz and company time zone as default

        Args:
         * tz_info - dict.
            EITHER (if timezone is manually selected):
             ** targetTz - name of chosen timezone
            OR (if timezone is )
             ** timeZoneOffset - int - difference of time from UTC in browser
             ** timeZoneName - char - name of timezone

        Methods:
         * get_possible_timezones_by_offset

        Returns:
         * list of timezones, char - timezone
        """
        tz_options = _tzs
        if tz_info.get("targetTz"):
            default_tz = tz_info.get("targetTz")
        else:
            default_tz = self.tz
        # 1
        if not default_tz:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            timezone_requried = safe_eval(ICPSudo.get_param('business_appointment_timezone_option', default='False'))
            if timezone_requried:
                # 2
                tz_name = tz_info.get("timeZoneName")
                for tz in tz_options:
                    if tz_name == tz[0]:
                        default_tz = tz_name
                        break
                else:
                    # 3
                    tz_offset = tz_info.get("timeZoneOffset") or 0
                    default_tz = get_possible_timezones_by_offset(tz_offset)
            else:
                # 4
                tz_options = []
                default_tz = self.env.user.sudo().company_id.partner_id.tz or self._context.get("tz")
        return tz_options, default_tz
