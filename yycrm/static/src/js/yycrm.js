openerp.yycrm = function(instance, local){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    // 实现弹出窗口可拖动 for admin
    instance.web.Dialog.include({
        open: function(){
            var self = this;
            this._super.apply(this, arguments);
            $('.modal.in').draggable({
                handle:'.modal-header'
            });
            return this;
        },
    });
    
    local.DashBoard = instance.Widget.extend({
        events: {
            'click .oe_yycrm_kanban_action': 'on_task_action_clicked',
            'click .o_dashboard_action': 'on_dashboard_action_clicked',
            'click .o_target_to_set': 'on_dashboard_target_clicked',
        },
        init: function (parent) {
            this._super(parent);
            this.domain = '["user_id","=", ' + instance.Widget.prototype.session.uid + ']';
            this.context = new instance.web.CompoundContext();
            this.groupbys = ['user_id'];
            this.mode =  "bar";
            this.model = new instance.web.Model('crm.lead');
            this.measures = {};

        },
        prepare_fields: function (fields) {
            var self = this;
            this.fields = fields;
            _.each(fields, function (field, name) {
                if ((name !== 'id') && (field.store === true)) {
                    if (field.type === 'integer' || field.type === 'float' || field.type === 'monetary') {
                        self.measures[name] = field;
                    }
                }
            });
            this.measures.__count__ = {string: _t("Quantity"), type: "integer"};
        },
        start: function(){
            var self = this;
            var model = new instance.web.Model('yycrm.task');
            

            model.call('new_retrieve_sales_dashboard', {context: new instance.web.CompoundContext()})
                .then(function(result){
                    self.show_demo = self.result && result['nb_opportunities'] == 0;
                    self.$el.append($(QWeb.render('dashboard', {
                        widget: self,
                        show_demo: self.show_demo,
                        values: result,
                    })));
                    self.model.call('fields_get', [], {context: new instance.web.CompoundContext()})
                        .then(function(result){
                            self.prepare_fields(result);
                                // .then(function(){
                            var test_widget = new openerp.mytest(self, new instance.web.Model('crm.lead'), {
                                measure: self.measures || '__count__',
                                mode: self.mode,
                                domain: self.domain,
                                groupbys: self.groupbys,
                                context: self.context,
                                fields: self.fields,
                                // stacked: self.fields_view.arch.attrs.stacked !== "False"
                            });
                            console.log(test_widget);
                            console.log(self.$el);
                            test_widget.appendTo(self.$el);
                                // });
                            }
                        )
                });

        },
        load_data: function () {
            var fields = this.groupbys.slice(0);
            if (this.measure !== '__count__'.slice(0))
                fields = fields.concat(this.measure);
            return this.model
                        .query(fields)
                        .filter(this.domain)
                        .context(this.context)
                        .lazy(false)
                        .group_by(this.groupbys.slice(0,2))
                        .then(this.proxy('prepare_data'));
        },
        prepare_data: function () {
            var raw_data = arguments[0],
                is_count = this.measure === '__count__';
            var data_pt, j, values, value;

            this.data = [];
            for (var i = 0; i < raw_data.length; i++) {
                data_pt = raw_data[i].attributes;
                values = [];
                if (this.groupbys.length === 1) data_pt.value = [data_pt.value];
                for (j = 0; j < data_pt.value.length; j++) {
                    values[j] = this.sanitize_value(data_pt.value[j], data_pt.grouped_on[j]);
                }
                value = is_count ? data_pt.length : data_pt.aggregates[this.measure];
                this.data.push({
                    labels: values,
                    value: value
                });
            }
        },
        sanitize_value: function (value, field) {
            if (value === false) return _t("Undefined");
            if (value instanceof Array) return value[1];
            if (field && this.fields[field] && (this.fields[field].type === 'selection')) {
                var selected = _.where(this.fields[field].selection, {0: value})[0];
                return selected ? selected[1] : value;
            }
            return value;
        },
        display_bar: function () {
            // prepare data for bar chart
            var data, values,
                measure = this.fields[this.measure].string;

            // zero groupbys
            if (this.groupbys.length === 0) {
                data = [{
                    values: [{
                        x: measure,
                        y: this.data[0].value}],
                    key: measure
                }];
            }
            // one groupby
            if (this.groupbys.length === 1) {
                values = this.data.map(function (datapt) {
                    return {x: datapt.labels, y: datapt.value};
                });
                data = [
                    {
                        values: values,
                        key: measure,
                    }
                ];
            }
            if (this.groupbys.length > 1) {
                var xlabels = [],
                    series = [],
                    label, serie, value;
                values = {};
                for (var i = 0; i < this.data.length; i++) {
                    label = this.data[i].labels[0];
                    serie = this.data[i].labels[1];
                    value = this.data[i].value;
                    if ((!xlabels.length) || (xlabels[xlabels.length-1] !== label)) {
                        xlabels.push(label);
                    }
                    series.push(this.data[i].labels[1]);
                    if (!(serie in values)) {values[serie] = {};}
                    values[serie][label] = this.data[i].value;
                }
                series = _.uniq(series);
                data = [];
                var current_serie, j;
                for (i = 0; i < series.length; i++) {
                    current_serie = {values: [], key: series[i]};
                    for (j = 0; j < xlabels.length; j++) {
                        current_serie.values.push({
                            x: xlabels[j],
                            y: values[series[i]][xlabels[j]] || 0,
                        });
                    }
                    data.push(current_serie);
                }
            }
            var svg = d3.select(this.$el[0]).append('svg');
            svg.datum(data);

            svg.transition().duration(0);

            var chart = nv.models.multiBarChart();
            chart.options({
              delay: 250,
              transition: 10,
              showLegend: _.size(data) <= MAX_LEGEND_LENGTH,
              showXAxis: true,
              showYAxis: true,
              rightAlignYAxis: false,
              stacked: this.stacked,
              reduceXTicks: false,
              // rotateLabels: 40,
              showControls: (this.groupbys.length > 1)
            });
            chart.yAxis.tickFormat(function(d) { return formats.format_value(d, { type : 'float' });});

            chart(svg);
            this.to_remove = chart.update;
            nv.utils.onWindowResize(chart.update);
        },
        on_task_action_clicked: function(ev){
            ev.preventDefault();

            var self = this;
            var $action = $(ev.currentTarget);
            var action_name = $action.attr('name');
            var action_extra = $action.data('id');
            var additional_context = {}

            new instance.web.Model("ir.model.data")
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

            new instance.web.Model("ir.model.data")
                .call("xmlid_to_res_id", [action_name])
                .then(function(data) {
                    if (data){
                       self.do_action(data, {additional_context: additional_context});
                    }
                });
        },
        render_monetary_field: function(value, currency_id) {
            var currency = instance.web.Widget.prototype.session.get_currency(currency_id);
            var digits_precision = currency && currency.digits;
            value = instance.web.format_value(value || 0, {type: "float", digits: digits_precision});
            if (currency) {
                if (currency.position === "after") {
                    value += currency.symbol;
                } else {
                    value = currency.symbol + value;
                }
            }
            return value;
        },
    });

    instance.web.client_actions.add('yycrm.dashboard', 'instance.yycrm.DashBoard');

    // console.log(require('sales_team.dashboard'));
    // var SalesTeamDashboardView = instance.sales_team.dashboard;
    // console.log(SalesTeamDashboardView);
    
    
};