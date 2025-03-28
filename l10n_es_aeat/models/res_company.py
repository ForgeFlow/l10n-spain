# Copyright 2019-2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models
from odoo.exceptions import UserError
from odoo.tools import ormcache

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    tax_agency_id = fields.Many2one("aeat.tax.agency", string="Tax Agency")

    @api.model_create_multi
    def create(self, vals_list):
        """Create immediately all the AEAT sequences when creating company."""
        companies = super().create(vals_list)
        models = (
            self.env["ir.model"]
            .sudo()
            .search([("model", "=like", "l10n.es.aeat.%.report")])
        )
        for model in models:
            try:
                self.env[model.model]._register_hook(companies=companies)
            except Exception as e:
                _logger.debug(e)
        return companies

    @ormcache("self", "xmlid")
    def _get_tax_id_from_xmlid(self, xmlid):
        """Low level cached search for a tax given its template XML-ID and company."""
        self.ensure_one()
        return (
            xmlid
            and self.sudo()
            .env["ir.model.data"]
            .search(
                [
                    ("model", "=", "account.tax"),
                    ("module", "=", "account"),  # All is registered under this module
                    ("name", "=", f"{self.id}_{xmlid}"),
                ]
            )
            .res_id
            or False
        )

    @ormcache("self", "xmlid")
    def _get_account_id_from_xmlid(self, xmlid):
        """Low level cached search for a tax given its account template and
        company.
        """
        self.ensure_one()
        return (
            xmlid
            and self.sudo()
            .env["ir.model.data"]
            .search(
                [
                    ("model", "=", "account.account"),
                    ("module", "=", "account"),  # All is registered under this module
                    ("name", "=", f"{self.id}_{xmlid}"),
                ]
            )
            .res_id
            or False
        )

    def get_certificates(self):
        company = self or self.env.user.company_id
        today = fields.Date.today()

        domain = [
            ("company_id", "=", company.id),
            "|",  # Or condition for date_start
            ("date_start", "=", False),
            ("date_start", "<=", today),
            "|",  # Or condition for date_end
            ("date_end", "=", False),
            ("date_end", ">=", today),
            ("state", "=", "active"),
        ]
        domain_aeat = [("scope", "=", "aeat")]
        domain_aeat = domain + domain_aeat

        aeat_certificate = self.env["certificate.certificate"].search(domain_aeat)
        if not aeat_certificate:
            aeat_certificate = self.env["certificate.certificate"].search(domain)
        if not aeat_certificate:
            raise UserError(self.env._("Error! There aren't certificates."))

        public_crt = aeat_certificate.pem_certificate
        private_key_record = aeat_certificate.private_key_id
        if not private_key_record or not private_key_record.pem_key:
            raise UserError(self.env._("Private key is missing or invalid."))

        private_key = private_key_record.pem_key

        return public_crt, private_key
