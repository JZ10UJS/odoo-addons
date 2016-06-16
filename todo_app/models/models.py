# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class todo_app(models.Model):
#     _name = 'todo_app.todo_app'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class TodoTask(models.Model):
    _name = 'todo.task'

    name = fields.Char('Description', required=True)
    is_done = fields.Boolean('Done?')
    active = fields.Boolean('Active?', default=True)

    @api.one
    def do_toggle_done(self):
        self.is_done = not self.is_done
        return True

    @api.multi
    def do_clear_done(self):
        done_recs = self.search([('is_done', '=', True)])
        done_recs.write({'active': False})
        return True

    state = fields.Selection([
        ('draft', u'草稿'),
        ('confirmed', u'审核中'),
        ('done', u'完成'),
    ], string=u'状态')


    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'


