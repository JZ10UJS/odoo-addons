# -*- coding: utf-8 -*-

from openerp import models, fields, api


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
        if partner_id:
            partner = self.env['res.partner'].browse([partner_id])
            data['value']['trade'] = partner.trade
        return data
        # values = {}
        # if partner_id:
        #     partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        #     partner_name = (partner.parent_id and partner.parent_id.name) or (
        #     partner.is_company and partner.name) or False
        #     values = {
        #         'partner_name': partner_name,
        #         'contact_name': (not partner.is_company and partner.name) or False,
        #         'title': partner.title and partner.title.id or False,
        #         'street': partner.street,
        #         'street2': partner.street2,
        #         'city': partner.city,
        #         'state_id': partner.state_id and partner.state_id.id or False,
        #         'country_id': partner.country_id and partner.country_id.id or False,
        #         'email_from': partner.email,
        #         'phone': partner.phone,
        #         'mobile': partner.mobile,
        #         'fax': partner.fax,
        #         'zip': partner.zip,
        #         'function': partner.function,
        #     }
        # return {'value': values}