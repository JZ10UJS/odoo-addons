odoo.define('yycrm.yykanban_column', function(require){
    "use strict";

    var config = require('web.config');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var form_common = require('web.form_common');
    var Widget = require('web.Widget');
    var quick_create = require('web_kanban.quick_create');
    var KanbanRecord = require('web_kanban.Record');

    var _t = core._t;
    var QWeb = core.qweb;
    var RecordQuickCreate = quick_create.RecordQuickCreate;

    var Column = require('web_kanban.Column');

    var YYKanban_Column = Column.extend({
        template: 'yycrm.Group',

        update_column: function () {
            var title = this.title + ' (' + this.records.length + ')';
            this.$header.find('.o_column_title').text(title);
            this.$header.find('.o-kanban-count').text(this.records.length);

            this.$el.toggleClass('o_column_folded', this.folded);
            var tooltip;
            if (this.remaining) {
                tooltip = this.records.length + '/' + this.dataset.size() + _t(' records');
            } else {
                tooltip = this.records.length + _t(' records');
            }
            tooltip = '<p>' + tooltip + '</p>' + this.tooltip_info;
            this.$header.tooltip({html: true}).attr('data-original-title', tooltip);
            if (!this.remaining) {
                this.$('.o_kanban_load_more').remove();
            } else {
                this.$('.o_kanban_load_more').html(QWeb.render('KanbanView.LoadMore', {widget:this}))
            }

            if (this.folded) {
                this.$('.row').hide();
            } else {
                this.$('.row').show();
                this.$('.o_column_revenue_count_all').text('￥ ' + this._get_total_planned_revenue(this.records));
            }
        },
        _get_total_planned_revenue: function(records){
            var total = 0;
            for (var i=0; i<records.length; i++){
                var tmp = records[i].record.planned_revenue.value.replace(/,/g, '');
                total += parseFloat(tmp);
            }
            var tmp1 = String(total).replace( /\B(?=(?:\d{3})+$)/g, ',' );
            if (tmp1[tmp1.length-3] !== '.'){
                return tmp1 + '.00';
            } else {
                return tmp1;
            }
        },
    });

    return YYKanban_Column;
});


odoo.define('yycrm.YYKanban', function(require){
    "use strict";

    var core = require('web.core');
    var data = require('web.data');
    var Model = require('web.DataModel');
    var Dialog = require('web.Dialog');
    var form_common = require('web.form_common');
    var Pager = require('web.Pager');
    var pyeval = require('web.pyeval');
    var session = require('web.session');
    var utils = require('web.utils');
    var View = require('web.View');

    var quick_create = require('web_kanban.quick_create');
    var KanbanRecord = require('web_kanban.Record');
    var kanban_widgets = require('web_kanban.widgets');

    var QWeb = core.qweb;
    var _lt = core._lt;
    var _t = core._t;
    var ColumnQuickCreate = quick_create.ColumnQuickCreate;
    var fields_registry = kanban_widgets.registry;


    var KanbanView = require('web_kanban.KanbanView');
    var YYKanbanColumn = require('yycrm.yykanban_column');


    var YYKanbanView = KanbanView.extend({
        display_name: _lt('YYKanban'),
        icon: 'fa fa-list-ul',
        view_type: "yykanban",
        render_grouped: function (fragment) {
            var self = this;

            // FORWARDPORT UP TO SAAS-10, NOT IN MASTER!
            // Drag'n'drop activation/deactivation
            var group_by_field_attrs = this.fields_view.fields[this.group_by_field];

            // Group_by field might not be in the Kanban view, so we need to get it somewhere else...
            // This somewhere else is on the search view.
            if (group_by_field_attrs === undefined) {
                if (this.ViewManager.searchview.groupby_menu && this.ViewManager.searchview.groupby_menu.groupable_fields) {
                    group_by_field_attrs = _.find(this.ViewManager.searchview.groupby_menu.groupable_fields, function(field) {
                        return field.name === self.group_by_field;
                    })
                }
            }
            // Deactivate the drag'n'drop if:
            // - field is a date or datetime since we group by month
            // - field is readonly
            var draggable = true;
            if (group_by_field_attrs) {
                if (group_by_field_attrs.type === "date" || group_by_field_attrs.type === "datetime") {
                    var draggable = false;
                }
                else if (group_by_field_attrs.readonly !== undefined) {
                    var draggable = !(group_by_field_attrs.readonly);
                }
            }
            var record_options = _.extend(this.record_options, {
                draggable: draggable,
            });

            var column_options = this.get_column_options();

            _.each(this.data.groups, function (group) {
                var column = new YYKanbanColumn(self, group, column_options, record_options);
                column.appendTo(fragment);
                self.widgets.push(column);
            });
            this.$el.sortable({
                axis: 'x',
                items: '> .o_kanban_group',
                handle: '.o_kanban_header',
                cursor: 'move',
                revert: 150,
                delay: 100,
                tolerance: 'pointer',
                forcePlaceholderSize: true,
                stop: function () {
                    var ids = [];
                    self.$('.o_kanban_group').each(function (index, u) {
                        ids.push($(u).data('id'));
                    });
                    self.resequence(ids);
                },
            });
            if (this.is_action_enabled('group_create') && this.grouped_by_m2o) {
                this.column_quick_create = new ColumnQuickCreate(this);
                this.column_quick_create.appendTo(fragment);
            }
            this.postprocess_m2m_tags();
        },
        add_new_column: function (event) {
            var self = this;
            var model = new Model(this.relation, this.search_context);
            model.call('create', [{name: event.data.value}], {
                context: this.search_context,
            }).then(function (id) {
                var dataset = new data.DataSetSearch(self, self.dataset.model, self.dataset.get_context(), []);
                var group_data = {
                    records: [],
                    title: event.data.value,
                    id: id,
                    attributes: {folded: false},
                    dataset: dataset,
                    values: {},
                };
                var options = self.get_column_options();
                var record_options = _.clone(self.record_options);
                var column = new YYKanbanColumn(self, group_data, options, record_options);
                column.insertBefore(self.$('.o_column_quick_create'));
                self.widgets.push(column);
                self.trigger_up('scrollTo', {selector: '.o_column_quick_create'});
            });
        },
        crm_display_members_names: function() {
            /*
             * Set avatar title for members.
             * In kanban views, many2many fields only return a list of ids.
             * We can implement return value of m2m fields like [(1,"Adminstration"),...].
             */
            var self = this;
            var members_ids = [];

            // Collect members ids
            self.$el.find('img[data-member_id]').each(function() {
                members_ids.push($(this).data('member_id'));
            });

            // Find their matching names
            var dataset = new data.DataSetSearch(self, 'res.users', session.context, [['id', 'in', _.uniq(members_ids)]]);
            dataset.read_slice(['id', 'name']).done(function(result) {
                _.each(result, function(v) {
                    // Set the proper value in the DOM
                    self.$el.find('img[data-member_id=' + v.id + ']').attr('title', v.name).tooltip();
                });
            });
        },
        on_groups_started: function() {
            var self = this;
            self._super.apply(self, arguments);

            if (self.dataset.model === 'crm.team') {
                self.crm_display_members_names();
            }
        },
    });

    core.view_registry.add('yykanban', YYKanbanView);

    return YYKanbanView;

    var KanbanRecord = require('web_kanban.Record');
    KanbanRecord.include({
        on_card_clicked: function() {
            if (this.model === 'crm.team') {
                this.$('.oe_kanban_crm_salesteams_list a').first().click();
            } else {
                this._super.apply(this, arguments);
            }
        },
    });
});


odoo.define('yycrm.sales_team_dashboard', function (require) {
    "use strict";

    var SalesTeamDashboardView = require('sales_team.dashboard');
    var Model = require('web.Model');

    SalesTeamDashboardView.include({

        events: {
            'click .o_yycrm_task_panel': 'on_task_action_clicked',
            'click .o_dashboard_action': 'on_dashboard_action_clicked',
            'click .o_target_to_set': 'on_dashboard_target_clicked',
        },

        fetch_data: function() {
            return new Model('yycrm.task')
                .call('retrieve_sales_dashboard', []);
        },

        on_task_action_clicked: function(ev){
            ev.preventDefault();

            var self = this;
            var $action = $(ev.currentTarget);
            var action_name = $action.attr('name');
            var action_extra = $action.data('id');
            var additional_context = {}

            new Model("ir.model.data")
                .call('xmlid_to_res_id', [action_name])
                .then(function(data){
                    if (data) {
                        self.do_action({
                            'views': [[false, 'form']],
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'yycrm.task',
                            'type': 'ir.actions.act_window',
                            'target': 'current',
                            'res_id': action_extra,
                        });
                    }
                });

        },
        on_dashboard_action_clicked: function(ev){
            ev.preventDefault();
    
            var self = this;
            var $action = $(ev.currentTarget);
            var action_name = $action.attr('name');
            var action_extra = $action.data('extra');
            var additional_context = {}
    
            // TODO: find a better way to add defaults to search view
            if (action_name === 'yycrm.yy_task_pivot_action') {
                additional_context = {'view_type':'pivot'};
            } else if (action_name === 'yycrm.yy_task_act_window_action') {
                if (action_extra === 'today') {
                    additional_context['search_default_today'] = 1;
                } else if (action_extra === 'this_week') {
                    additional_context['search_default_this_week'] = 1;
                } else if (action_extra === 'overdue') {
                    additional_context['search_default_overdue'] = 1;
                }
            } else if (action_name === 'crm.crm_opportunity_report_action_graph') {
                additional_context['search_default_won'] = 1;
            }
    
            new Model("ir.model.data")
                .call("xmlid_to_res_id", [action_name])
                .then(function(data) {
                    if (data){
                       self.do_action(data, {additional_context: additional_context});
                    }
                });
        },
    });

});