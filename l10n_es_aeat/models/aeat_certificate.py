# (c) 2017 Diagram Software S.L.
# (c) 2017 Consultoría Informática Studio 73 S.L.
# (c) 2019 Acysos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import exceptions, fields, models


class L10nEsAeatCertificate(models.Model):
    _name = "l10n.es.aeat.certificate"
    _description = "AEAT Certificate"

    name = fields.Char()
    state = fields.Selection(
        selection=[("draft", "Draft"), ("active", "Active")],
        default="draft",
    )
    certificate_id = fields.Many2one(
        comodel_name="certificate.certificate",
        string="Certificate",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    date_start = fields.Datetime(related="certificate_id.date_start")
    date_end = fields.Datetime(related="certificate_id.date_end")

    def action_active(self):
        self.ensure_one()
        other_configs = self.search(
            [("id", "!=", self.id), ("company_id", "=", self.company_id.id)]
        )
        for config_id in other_configs:
            config_id.state = "draft"
        self.state = "active"

    def get_certificates(self, company=False):
        if not company:
            company = self.env.user.company_id
        today = fields.Date.today()
        aeat_certificate = self.search(
            [
                ("company_id", "=", company.id),
                ("certificate_id", "!=", False),
                "|",
                ("certificate_id.date_start", "=", False),
                ("certificate_id.date_start", "<=", today),
                "|",
                ("certificate_id.date_end", "=", False),
                ("certificate_id.date_end", ">=", today),
                ("state", "=", "active"),
            ],
            limit=1,
        )
        if not aeat_certificate:
            raise exceptions.UserError(self.env._("Error! There aren't certificates."))

        public_crt = aeat_certificate.certificate_id.pem_certificate
        private_key_record = aeat_certificate.certificate_id.private_key_id
        if not private_key_record or not private_key_record.pem_key:
            raise exceptions.UserError(self.env._("Private key is missing or invalid."))

        private_key = private_key_record.pem_key

        return public_crt, private_key
