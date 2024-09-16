# -*- coding: utf-8 -*-
# Part of Keypress IT Services. See LICENSE file for full copyright and licensing details.##
##################################################################################
from odoo import api, fields, models

class amount_spt(models.Model):
    _name = 'amount.spt'
    _description = 'Payment Split'
    _rec_name = 'amount'
    
    amount = fields.Monetary(string='Payment Amount',currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True)
    journal_id = fields.Many2one('account.journal', string='Payment Journal', readonly=False)
    payment_split_id = fields.Many2one('payment.split.spt','Payment')
    amount_currency = fields.Monetary(string='Amount Due',currency_field='currency_id',readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=False,default=lambda self: self.env.company)

    @api.model
    def default_get(self,default_fields):
        res = super(amount_spt, self).default_get(default_fields)
        res.update({'journal_id':self.journal_id.search([('type','=','cash')],limit=1).id})
        return res
    
    

    # def recalculate_amount_currency_onchange_amount(self,old_pay_diff,new_pay_diff):
    #     for line in self:
    #         if old_pay_diff:
    #             line.amount_currency = (new_pay_diff * line.amount_currency) / old_pay_diff
            
    def recalculate_amount_currency_onchange_amount(self,paydiff):
        for line in self:
            rate = self.env['res.currency']._get_conversion_rate(
                    from_currency = line.company_id.currency_id,
                    to_currency = line.payment_split_id.currency_id,
                    company = line.company_id,
                    date = line.payment_split_id.move_ids[0].invoice_date or fields.Date.context_today(line)
                )
            line_rate = self.env['res.currency']._get_conversion_rate(
                    from_currency = line.company_id.currency_id,
                    to_currency = line.currency_id,
                    company = line.company_id,
                    date = line.payment_split_id.move_ids[0].invoice_date or fields.Date.context_today(line)
                )
            line.amount_currency = (paydiff / rate) * line_rate
    
    @api.onchange('journal_id')
    def _onchange_amount_ids(self):
        for record in self:
            if record.payment_split_id:
                record.currency_id = record.journal_id.currency_id if record.journal_id.currency_id else record.payment_split_id.move_ids[0].currency_id

    