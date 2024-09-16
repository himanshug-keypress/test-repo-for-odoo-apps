# -*- coding: utf-8 -*-
# Part of Keypress IT Services. See LICENSE file for full copyright and licensing details.##
##################################################################################
from odoo import api, fields, models

class payment_split_spt(models.Model):
    _name = 'payment.split.spt'
    _description = 'Payment Split'

    amount_ids = fields.One2many('amount.spt', 'payment_split_id','Payment Amounts')
    move_ids = fields.Many2many('account.move','payment_split_spt_account_move_rel','payment_split_id','move_id','Invoice')
    partner_id = fields.Many2one('res.partner', string='Partner')

    company_id = fields.Many2one('res.company', string='Company',default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency')

    payment_difference = fields.Monetary(currency_field='currency_id', store=True,compute='_compute_payment_difference')
    payment_difference_handling = fields.Selection([('open', 'Keep open'), ('reconcile', 'Mark invoice as fully paid')],
        default='open',
        string="Payment Difference Handling")
    
    writeoff_account_id = fields.Many2one('account.account',
                                          string="Difference Account",
                                          domain=[('deprecated', '=', False)],
                                          copy=False)
    writeoff_label = fields.Char(
        string='Journal Item Label',
        help=
        'Change label of the counterpart that will hold the payment difference',
        default='Write-Off')

    @api.depends('move_ids', 'amount_ids')
    def _compute_payment_difference(self):
        total_invoice_amount = 0
        total_amount = 0
        amount_amount = 0
        for record in self:
            # old_pay_diff = record.payment_difference
            for invoice in record.move_ids:
                try:
                    total_invoice_amount = total_invoice_amount + invoice._origin.amount_residual
                except:
                    total_invoice_amount = total_invoice_amount + invoice.amount_residual
            for amount in record.amount_ids:
                amount_amount = amount.amount
                if amount.journal_id.currency_id and amount.currency_id != record.currency_id:
                    amount_amount = amount.journal_id.currency_id._convert(amount_amount,record.currency_id,self.company_id,fields.Date.context_today(self))
               
                if record.move_ids[0].move_type in ('out_invoice','in_refund'):
                    total_amount = total_amount + amount_amount
                if record.move_ids[0].move_type in ('out_refund', 'in_invoice'):
                    total_amount = total_amount - abs(amount_amount)

            record.payment_difference = total_invoice_amount - total_amount
            # if not record.payment_difference == record.move_ids[0].amount_residual:
            record.amount_ids.recalculate_amount_currency_onchange_amount(record.payment_difference)

    def payment_post(self):
        lines = self.amount_ids.filtered(lambda a:a.amount != 0)
        for line in lines:
            payment_difference_handling  = 'open'
            if line == lines[-1] and self.payment_difference != 0.0 and self.payment_difference_handling == 'reconcile':
                payment_difference_handling = 'reconcile'

            account_payment_register_id = self.env['account.payment.register'].create(
                {
                    'journal_id' : line.journal_id.id,
                    'amount' : line.amount,
                    'communication' : self.move_ids[0].name,
                    'payment_difference_handling' : payment_difference_handling,
                    'writeoff_account_id' : self.writeoff_account_id.id if self.writeoff_account_id and payment_difference_handling == 'reconcile' else False
                }
            )
            if account_payment_register_id:
                account_payment_register_id.action_create_payments()
