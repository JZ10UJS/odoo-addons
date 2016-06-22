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
                                     ('confirmed', u'待审核'),
                                     ('done', u'通过'),
    ], string=u'折扣申请', default='draft', readonly=True)

    @api.multi
    def ask_for_more_discount(self):
        self.new_state = 'confirmed'

    @api.multi
    def allow_for_more_discount(self):
        self.new_state = 'done'

    @api.multi
    def reject_for_more_discount(self):
        self.new_state = 'draft'

    need_ask = fields.Boolean(compute='check_discount', default=False)

    @api.multi
    @api.depends('order_line.discount')
    def check_discount(self):
        self.ensure_one()
        max_discount = self.order_line and max(i.discount for i in self.order_line) or 0
        min_discount = self.order_line and min(i.discount if i else 0 for i in self.order_line) or 0
        if min_discount < 0:
            raise exceptions.ValidationError('The discount can not be negative.')

        if self.env.ref('base.group_sale_salesman_all_leads').id not in self.env.user.groups_id.ids:
            if  max_discount > 5:
                self.need_ask = True
        else:
            if max_discount > 10:
                self.need_ask = True




