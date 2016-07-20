# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, osv, tools



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


class Task(models.Model):
    _name = 'yycrm.task'

    name = fields.Char(string='Next Task', required=True)
    opportunity_id = fields.Many2one('crm.lead', string='Opportunity', required=True)
    date_deadline = fields.Date(string='Date Deadline', required=True)
    is_done = fields.Boolean(string='Done?', default=False)

    customer_id = fields.Many2one('res.partner', string='Customer')
    city = fields.Char(string='City')
    street = fields.Char(string='Street')
    phone = fields.Char(string='Phone')
    mobile = fields.Char(string='Mobile')
    email = fields.Char(string='Email')

    @api.one
    def mark_done(self):
        for record in self:
            record.write({'is_done': True})
        return True

    @api.multi
    def one_change_opportunity_id(self, oppor_id):
        values = {}
        if oppor_id:
            oppor = self.env['crm.lead'].browse([oppor_id])
            partner = oppor.partner_id
            values = {
                'customer_id': partner,
                'street': partner.street,
                'city': partner.city,
                'email': partner.email,
                'phone': partner.phone,
                'mobile': partner.mobile,
                'function': partner.function,
            }
        return {'value': values}

    def retrieve_sales_dashboard(self, cr, uid, context=None):
        # print cr, uid
        # data = super(Leads, self).retrieve_sales_dashboard(cr, uid, context=context)
        # return data
        res = {
            'meeting': {
                'today': 0,
                'next_7_days': 0,
            },
            'activity': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'closing': {
                'today': 0,
                'overdue': 0,
                'next_7_days': 0,
            },
            'done': {
                'this_month': 0,
                'last_month': 0,
            },
            'won': {
                'this_month': 0,
                'last_month': 0,
            },
            'nb_opportunities': 0,
        }

        opportunities = self.pool['crm.lead'].search_read(cr, uid,
                                         [('type', '=', 'opportunity'), ('user_id', '=', uid)],
                                         ['date_deadline', 'planned_revenue', 'date_closed'], context=context)
        for opp in opportunities:

            # Expected closing
            if opp['date_deadline']:
                date_deadline = datetime.strptime(opp['date_deadline'], tools.DEFAULT_SERVER_DATE_FORMAT).date()

                if date_deadline == date.today() and not opp['date_closed']:
                    res['closing']['today'] += 1
                if date.today() + timedelta(days=7) >= date_deadline >= date.today() and not opp['date_closed']:
                    res['closing']['next_7_days'] += 1
                if date_deadline < date.today() and not opp['date_closed']:
                    res['closing']['overdue'] += 1

            # Won in Opportunities
            if opp['date_closed']:
                date_closed = datetime.strptime(opp['date_closed'], tools.DEFAULT_SERVER_DATETIME_FORMAT).date()

                if date.today().replace(day=1) <= date_closed <= date.today():
                    if opp['planned_revenue']:
                        res['won']['this_month'] += opp['planned_revenue']
                elif date.today().replace(day=1) - relativedelta(months=+1) <= date_closed < date.today().replace(
                        day=1):
                    if opp['planned_revenue']:
                        res['won']['last_month'] += opp['planned_revenue']

        task_done = self.pool('yycrm.task').search_read(cr, uid, [('create_uid', '=', uid), ('is_done', '=', True)],
                                                        ['date_deadline'])
        for act in task_done:
            if act['date_deadline']:
                date_act = datetime.strptime(act['date_deadline'], tools.DEFAULT_SERVER_DATE_FORMAT).date()
                if date_act <= date.today().replace(day=1) - relativedelta(
                        months=-1) and date_act >= date.today().replace(day=1):
                    res['done']['this_month'] += 1
                elif date_act < date.today().replace(day=1) and date_act >= date.today().replace(day=1) - relativedelta(
                        months=+1):
                    res['done']['last_month'] += 1

        task_not_done = self.pool('yycrm.task').search_read(cr, uid,
                                                            [('create_uid', '=', uid), ('is_done', '=', False)],
                                                            ['date_deadline', 'opportunity_id', 'name'],
                                                            order='date_deadline')
        res['task_not_done'] = task_not_done
        for act in task_not_done:
            date_act = datetime.strptime(act['date_deadline'], tools.DEFAULT_SERVER_DATE_FORMAT).date()
            if date_act == date.today():
                res['activity']['today'] += 1
            if date_act >= date.today() and date_act <= date.today() + timedelta(days=7):
                res['activity']['next_7_days'] += 1
            if date_act < date.today():
                res['activity']['overdue'] += 1

        res['nb_opportunities'] = len(opportunities)

        user = self.pool('res.users').browse(cr, uid, uid, context=context)
        res['done']['target'] = user.target_sales_done
        res['won']['target'] = user.target_sales_won

        res['currency_id'] = user.company_id.currency_id.id

        return res

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

class CrmTeam(models.Model):
    _inherit = 'crm.team'

    def action_your_pipeline(self, cr, uid, context=None):
        IrModelData = self.pool['ir.model.data']
        action = IrModelData.xmlid_to_object(cr, uid, 'crm.crm_lead_opportunities_tree_view', context=context).read(
            ['name', 'help', 'res_model', 'target', 'domain', 'context', 'type', 'search_view_id'])
        if not action:
            action = {}
        else:
            action = action[0]

        user_team_id = self.pool['res.users'].browse(cr, uid, uid, context=context).sale_team_id.id
        if not user_team_id:
            user_team_id = self.search(cr, uid, [], context=context, limit=1)
            user_team_id = user_team_id and user_team_id[0] or False
            action['help'] = """<p class='oe_view_nocontent_create'>Click here to add new opportunities</p><p>
            Looks like you are not a member of a sales team. You should add yourself
            as a member of one of the sales team.\n</p>"""
            if user_team_id:
                action['help'] += "<p>As you don't belong to any sales team, Odoo opens the first one by default.</p>"

        print action['context']
        action_context = eval(action['context'], {'uid': uid})
        if user_team_id:
            action_context.update({
                'default_team_id': user_team_id,
                'search_default_team_id': user_team_id
            })

        tree_view_id = IrModelData.xmlid_to_res_id(cr, uid, 'crm.crm_case_tree_view_oppor')
        form_view_id = IrModelData.xmlid_to_res_id(cr, uid, 'crm.crm_case_form_view_oppor')
        # 修改这两处，用以实现对pipeline的外观修改
        kanb_view_id = IrModelData.xmlid_to_res_id(cr, uid, 'yycrm.yy_pipeline_view_kanban_inherited')
        action.update({
            'views': [
                [kanb_view_id, 'yykanban'],
                [tree_view_id, 'tree'],
                [form_view_id, 'form'],
                [False, 'graph'],
                [False, 'calendar'],
                [False, 'pivot']
            ],
            'context': action_context,
        })
        return action
