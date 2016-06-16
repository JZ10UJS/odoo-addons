# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions

# class todo_ui(models.Model):
#     _name = 'todo_ui.todo_ui'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class Tag(models.Model):
    _name = 'todo.task.tag'
    _parent_store = True

    name = fields.Char('Name', size=40)
    task_ids = fields.Many2many('todo.task', string='Tasks')
    parent_id = fields.Many2one('todo.task.tag', 'Parent Tag', ondelte='restrict')
    parent_left = fields.Integer('Parent Left', index=True)
    parent_right = fields.Integer('Parent Right', index=True)
    child_ids = fields.One2many('todo.task.tag', 'parent_id', string='Child Tags')


class Stage(models.Model):
    _name = 'todo.task.stage'
    _order = 'sequence,name'

    name = fields.Char('Name', size=40)
    sequence = fields.Integer('Sequence')
    desc = fields.Text('Description')
    state = fields.Selection([('draft','New'), ('open', 'Started'), ('done', 'Closed')], string='State')
    docs = fields.Html('Documentation')
    perc_complete = fields.Float('% Complete', (3,2))

    data_effective = fields.Date('Effective Date')
    date_changed = fields.Datetime('Last Changed')

    fold = fields.Boolean('Folded?')
    image = fields.Binary('Image')
    tasks = fields.One2many('todo.task', 'stage_id', 'Tasks in this stage')


class TodoTask(models.Model):
    _inherit = 'todo.task'
    _sql_constraints = [('todo_task_name_uniq', 'UNIQUE(name, user_id, active)', 'Task title must be unique!')]

    stage_id = fields.Many2one('todo.task.stage', 'Stage')
    tag_ids = fields.Many2many('todo.task.tag', 'Tags')
    stage_fold = fields.Boolean('Stage Fold?',
                                compute='_compute_stage_fold',
                                search='_search_stage_fold',
                                inverse='_write_stage_fold')
    stage_state = fields.Selection(related='stage_id.state', string='Stage state')

    effort_estimate = fields.Integer('Effort Estimate')

    @api.one
    @api.depends('stage_id.fold')
    def _compute_stage_fold(self):
        self.stage_fold = self.stage_id.fold

    def _search_stage_fold(self, operator, value):
        return [('stage_id.fold', operator, value)]

    def _write_stage_fold(self):
        self.stage_id.fold = self.stage_fold

    @api.one
    @api.constrains('name')
    def _check_name_size(self):
        if len(self.name) < 5:
            raise exceptions.ValidationError('Must have 5 chars!')

    @api.one
    def compute_user_todo_count(self):
        self.user_todo_count = self.search_count([('user_id','=',self.user_id.id)])

    user_todo_count = fields.Integer('User To-Do Count', compute=compute_user_todo_count)
