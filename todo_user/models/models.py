# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class todo_user(models.Model):
#     _name = 'todo_user.todo_user'

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
    _inherit = ['todo.task', 'mail.thread']

    name = fields.Char(help='What needs to be done?')
    user_id = fields.Many2one('res.users', string='Responsible')
    date_deadline = fields.Date(string='Deadline')

    @api.multi
    def do_clear_done(self):
        domain = [('is_done', '=', True),
                '|', ('user_id', '=', self.env.uid),
                ('user_id', '=', False)]
        done_recs = self.search(domain)
        done_recs.write({'active': False})
        return True

    @api.one
    def do_toggle_done(self):
        if self.user_id != self.env.user:
            raise Exception('Only the responsible can do this!')
        else:
            return super(TodoTask, self).do_toggle_done()

