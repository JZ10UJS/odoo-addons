# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions


# class mycrm(models.Model):
#     _name = 'mycrm.mycrm'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


# class MyOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     @api.multi
#     @api.constrains('discount')
#     def do_check_discount(self):
#         self.ensure_one()
#         if self.env.ref('base.group_sale_salesman_all_leads').id not in self.env.user.groups_id.ids:
#             if self.discount < 0 or self.discount > 5:
#                 raise exceptions.ValidationError('The discount must lower than 5.00%.')
#         else:
#             if self.discount < 0 or self.discount > 10:
#                 raise exceptions.ValidationError('The discount must lower than 10.00%.')


class MyOrder(models.Model):
    _inherit = 'sale.order'

    new_state = fields.Selection([
                                     ('draft', u'草稿'),
                                     ('confirmed1', u'待审核'),
                                     ('confirmed2', u'管理部审核'),
                                     ('done', u'通过'),
    ], string=u'折扣申请', default='draft', readonly=True)

    @api.multi
    def ask_for_more_discount(self):
        self.new_state = 'confirmed1'

    @api.multi
    def allow_for_more_discount(self):
        if self.env.ref('base.group_sale_manager').id in self.env.user.groups_id.ids:
            # 此人在 sales/manager 组中，无论折扣多少可以直接同意。
            self.new_state = 'done'
            self.need_ask = False
        elif self.env.ref('base.group_sale_salesman_all_leads').id in self.env.user.groups_id.ids:
            if max(i.discount for i in self.order_line) <= 10:
                self.new_state = 'done'
                self.need_ask = False
            else:
                raise exceptions.ValidationError('The discount is greater than 10%, You must ask for superior.')

    @api.multi
    def ask_for_more_discount2(self):
        if self.env.ref('base.group_sale_salesman_all_leads').id in self.env.user.groups_id.ids:
            self.new_state = 'confirmed2'

    @api.multi
    def reject_for_more_discount(self):
        self.new_state = 'draft'

    need_ask = fields.Boolean(compute='check_discount',default=False)

    @api.one
    @api.depends('order_line.discount')
    def check_discount(self):
        max_discount = self.order_line and max(i.discount for i in self.order_line) or 0
        min_discount = self.order_line and min(i.discount if i else 0 for i in self.order_line) or 0
        if min_discount < 0:
            raise exceptions.ValidationError('The discount can not be negative.')

        if self.env.ref('base.group_sale_salesman_all_leads').id not in self.create_uid.groups_id.ids:
            if  max_discount > 5 and self.new_state != 'done':
                self.need_ask = True
            else:
                self.new_state = 'done'
        else:
            if max_discount > 10 and self.new_state != 'done':
                self.need_ask = True
            else:
                self.new_state = 'done'



class MyOrderLine(models.Model):
    _inherit = 'sale.order.line'

    _help_field = fields.Char(compute='_do_check_discount')

    @api.one
    @api.depends('discount')
    def _do_check_discount(self):
        self.order_id.new_state='draft'
        self.order_id.check_discount()


