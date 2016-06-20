# -*- coding: utf-8 -*-

from openerp import models, fields, api

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

class MyCustomer(models.Model):
    _inherit = 'res.partner'

    show_cus_type = fields.Char(string='TYPE',compute='_compute_type')

    @api.one
    @api.depends('company_type')
    def _compute_type(self):
        self.show_cus_type = self.company_type