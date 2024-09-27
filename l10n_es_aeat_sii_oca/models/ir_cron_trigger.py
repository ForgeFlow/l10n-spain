# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class IrCronTrigger(models.Model):
    _inherit = "ir.cron.trigger"

    def _get_aeat_time_field(self):
        time_field = super()._get_aeat_time_field()
        if not time_field:
            sii_send_cron = self.env.ref(
                "l10n_es_aeat_sii_oca.invoice_send_to_sii", False
            )
            if sii_send_cron and self.cron_id == sii_send_cron:
                time_field = "sii_send_date"
        return time_field

    def _get_aeat_account_moves(self):
        moves = super()._get_aeat_account_moves()
        if not moves:
            sii_send_cron = self.env.ref(
                "l10n_es_aeat_sii_oca.invoice_send_to_sii", False
            )
            if sii_send_cron and self.cron_id == sii_send_cron:
                moves = self.env["account.move"].search(
                    [("sii_invoice_cron_trigger_ids", "in", [self.id])]
                )
        return moves

    def _get_aeat_sending_time(self, account_move):
        sending_time = super()._get_aeat_sending_time(account_move)
        if not sending_time:
            sii_send_cron = self.env.ref(
                "l10n_es_aeat_sii_oca.invoice_send_to_sii", False
            )
            if sii_send_cron and self.cron_id == sii_send_cron:
                sending_time = account_move.company_id._get_sii_sending_time()
        return sending_time
