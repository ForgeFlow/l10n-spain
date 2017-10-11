# -*- coding: utf-8 -*-
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.

from odoo import api, models, _
from odoo.exceptions import ValidationError


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    @api.constrains('company_id')
    def journal_invoice_sequence_company_constrains(self):
        for rec in self:
            journal_inv = rec.env['account.journal'].search(
                [('invoice_sequence_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if journal_inv:
                raise ValidationError(_(
                    "This sequence is already being used as Invoice sequence "
                    "in journal '%s', that belongs to another company." %
                    journal_inv.name))
            journal_refund = rec.env['account.journal'].search(
                [('refund_inv_sequence_id', '=', rec.id),
                 ('company_id', '!=', False),
                 ('company_id', '!=', rec.company_id.id)], limit=1)
            if journal_refund:
                raise ValidationError(_(
                    "This sequence is already being used as Refund sequence "
                    "in journal '%s', that belongs to another company." %
                    journal_refund.name))
