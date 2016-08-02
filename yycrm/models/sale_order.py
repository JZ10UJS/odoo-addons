#!/usr/bin/python
# coding: utf-8


from openerp import api, models, fields, exceptions
import openerp.addons.decimal_precision as dp


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     state = fields.Selection([
#         ('draft', 'Quotation'),
#         ('sent', 'Quotation Sent'),
#         ('sale', 'Sale Order'),
#         ('done', 'Done'),
#         ('cancel', 'Cancelled'),
#     ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')
#
#     permission_status = fields.Selection([
#         ('p_draft', u'草稿'),
#         ('p_confirm1', u'区域审核'),
#         ('p_confirm2', u'管理部审核'),
#         ('p_done', u'审核通过'),
#     ], string=u'折扣申请状态', default='p_draft', track_visibility='onchange', store=True)
#
#     need_permission = fields.Boolean(compute='_check_discount', default=False)
#
#     @api.depends('order_line.discount')
#     def _check_discount(self):
#
#         max_discount = self.order_line and max(i.discount for i in self.order_line) or 0
#         u_discount = self.create_uid.max_discount or self.create_uid.sale_team_id.max_discount
#
#         if max_discount > u_discount and self.permission_status != 'p_done':
#             self.need_permission = True
#         else:
#             self.permission_status = 'p_done'
#
#     @api.multi
#     def p_action_draft(self):
#         self.write({'permission_status': 'p_draft'})
#
#     @api.multi
#     def p_action_confirm1(self):
#         self.write({'permission_status': 'p_confirm1'})
#
#     @api.multi
#     def p_action_confirm2(self):
#         self.write({'permission_status': 'p_confirm2'})
#
#     @api.multi
#     def p_action_done(self):
#         self.write({'permission_status': 'p_done'})


class MyOrder(models.Model):
    _inherit = 'sale.order'

    new_state = fields.Selection([
                                     ('draft', u'草稿'),
                                     ('confirmed1', u'待审核'),
                                     ('confirmed2', u'管理部审核'),
                                     ('done', u'通过'),
    ], string=u'折扣申请', default='draft', track_visibility='onchange')

    pre_sales_engineer_ids = fields.Many2many('res.users', string='Pre-sales Engineers')

    @api.multi
    def ask_for_more_discount(self):
        self.ensure_one()
        self.new_state = 'confirmed1'

    @api.multi
    def allow_for_more_discount(self):
        self.ensure_one()
        u_discount = self.env.user.max_discount or self.env.user.sale_team_id.max_discount
        if self.env.ref('base.group_sale_manager').id in self.env.user.groups_id.ids:
            # 此人在 sales/manager 组中，无论折扣多少可以直接同意。
            self.write({
                'new_state': 'done',
                'need_ask': False,
            })
        elif self.env.ref('base.group_sale_salesman_all_leads').id in self.env.user.groups_id.ids:
            if max(i.discount for i in self.order_line) <= u_discount:
                self.write({
                    'new_state': 'done',
                    'need_ask': False,
                })
            else:
                raise exceptions.ValidationError('You must ask for permission.')

    @api.multi
    def ask_for_more_discount2(self):
        self.ensure_one()
        if self.env.ref('base.group_sale_salesman_all_leads').id in self.env.user.groups_id.ids:
            self.new_state = 'confirmed2'

    @api.multi
    def reject_for_more_discount(self):
        self.ensure_one()
        self.new_state = 'draft'

    need_ask = fields.Boolean(compute='check_discount', default=False, store=True)

    @api.multi
    @api.depends('order_line.discount')
    def check_discount(self):
        max_discount = self.order_line and max(i.discount for i in self.order_line) or 0

        # if self.env.ref('base.group_sale_salesman_all_leads').id not in self.create_uid.groups_id.ids:
        #     if  max_discount > 5 and self.new_state != 'done':
        #         self.need_ask = True
        #     else:
        #         self.new_state = 'done'
        # else:
        #     if max_discount > 10 and self.new_state != 'done':
        #         self.need_ask = True
        #     else:
        #         self.new_state = 'done'

        u_discount = self.user_id.max_discount or self.user_id.sale_team_id.max_discount

        if max_discount > u_discount:
            if self.new_state != 'done':
                self.need_ask = True
            else:
                self.new_state = 'draft'
                self.need_ask = True
        else:
            self.need_ask = False
            self.new_state = 'done'

    @api.onchange('order_line')
    def do_check(self):
        self.new_state = 'draft'


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    discount = fields.Float(string='Discount (% off)', digits=dp.get_precision('Discount'), default=0.0)