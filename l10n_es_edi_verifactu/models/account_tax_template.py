from odoo import _, api, fields, models


class AccountTaxTemplate(models.Model):
    _inherit = "account.tax.template"

    l10n_es_applicability = fields.Selection(
        selection=[
            ("01", "VAT"),
            ("02", "IPSI"),
            ("03", "IGIC"),
        ],
        string="Applicability (Spain)",
    )

    def _get_tax_vals(self, company, tax_template_to_tax):
        val = super()._get_tax_vals(company, tax_template_to_tax)
        val["l10n_es_applicability"]: self.l10n_es_applicability
        return val
