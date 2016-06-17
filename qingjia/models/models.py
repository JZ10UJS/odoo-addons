# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import timedelta

# class qingjia(models.Model):
#     _name = 'qingjia.qingjia'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class QingjiaDan(models.Model):
    _name = 'qingjia.qingjd'

    name = fields.Char(string=u'标题')
    reason = fields.Text(string=u'原因')
    date_start = fields.Datetime(string=u'开始时间', default=fields.Datetime.now)
    date_end = fields.Datetime(string=u'结束时间', compute='_compute_date_end', inverse='_write_days')
    days = fields.Float(string=u'天数', default=1.0)

    state = fields.Selection([
        ('refuse', u'不通过'),
        ('draft', u'草稿'),
        ('confirmed', u'待审核'),
        ('done', u'通过'),
    ], string='State')

    @api.depends('date_start', 'days')
    def _compute_date_end(self):
        s_date = fields.Datetime.from_string(self.date_start)
        self.date_end = s_date + timedelta(days=self.days)


    @api.onchange
    def _write_days(self):
        s_date = fields.Datetime.from_string(self.date_start)
        e_date = fields.Datetime.from_string(self.date_end)
        self.days = (e_date - s_date).days + 1.0


    @api.multi
    def do_draft(self):
        self.state = 'draft'

    @api.multi
    def do_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def do_refuse(self):
        self.state = 'refuse'

    @api.multi
    def do_done(self):
        self.state = 'done'

