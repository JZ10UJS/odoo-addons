# -*- coding: utf-8 -*-

from openerp import models, fields, api, osv


class Department(models.Model):
    _name = 'yycrm.department'

    name = fields.Char(string='description')


class Trade(models.Model):
    _name = 'yycrm.trade'

    name = fields.Char(string='description')


class ProjectChannels(models.Model):
    _name = 'yycrm.channel'

    name = fields.Char(string='description')


class Solution(models.Model):
    _name = 'yycrm.solution'

    name = fields.Char(string='description')


class View(osv.osv.osv):
    _inherit = 'ir.ui.view'

    def __init__(self, pool, cr):
        super(View, self).__init__(pool, cr)
        if 'yykanban' not in [i[0] for i in super(View, self)._columns['type'].selection]:
            super(View, self)._columns['type'].selection.append(('yykanban','YYKanbanView'))


class Partner(models.Model):
    _inherit = 'res.partner'

    department = fields.Many2one('yycrm.department', string='Department')
    trade = fields.Many2one('yycrm.trade',string='Trade')


class Leads(models.Model):
    _inherit = 'crm.lead'

    trade = fields.Many2one('yycrm.trade', string='Trade')
    channel_id = fields.Many2one('yycrm.channel', string='Project Channel')
    solution_ids = fields.Many2many('yycrm.solution', string='Solution')
    product_ids = fields.Many2many('product.product', string='Products')
    pre_sales_engineer_ids = fields.Many2many('res.users', string='Pre-sales Engineer')

    @api.multi
    def on_change_partner_id(self, partner_id):
        data = super(Leads, self).on_change_partner_id(partner_id)
        partner = self.env['res.partner'].browse([partner_id])
        data['value']['trade'] = partner.trade
        return data