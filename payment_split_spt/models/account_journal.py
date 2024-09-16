from odoo import models, fields

class account_journal(models.Model):
    _inherit = 'account.journal'
    
    default_use = fields.Boolean('Use Default For Multiple Payments')