# -*- coding: utf-8 -*-
# Part of Keypress IT Services. See LICENSE file for full copyright and licensing details.##
##################################################################################

from odoo import models,fields, _

class account_move(models.Model):
    _inherit = 'account.move'

    def action_invoice_register_payment(self):
        form_view = self.env.ref('payment_split_spt.payment_split_form_view_spt')

        for record in self:
            line_vals=[]
            journal_ids = self.env['account.journal'].search([('default_use','=',True)])
            for journal in journal_ids:
                currency = journal.currency_id
                if not journal.currency_id:
                    currency = record.currency_id
                # amt = record.currency_id._convert(record.amount_residual,currency,record.company_id,record.invoice_date)
                amount_vals = {
                                'amount': 0.0,
                                # 'amount_currency' : amt,
                                'currency_id': currency.id,
                                'journal_id': journal.id
                }
                line_vals.append([0, 0, amount_vals])
            res_id = self.env['payment.split.spt'].create({
                'move_ids' : [(4,rec.id) for rec in self],
                'currency_id' : self.currency_id.id,
                'partner_id' : record.partner_id.id,
                'amount_ids' : line_vals
                })
            
        return {
        'name': _('Register Payment'),
        'view_type': 'form',
        'view_mode': 'form',
        'res_model': 'payment.split.spt',
        'views': [(form_view.id, 'form')],
        'type': 'ir.actions.act_window',
        'target': 'new',
        'res_id' : res_id.id
      }


