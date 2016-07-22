openerp.oepetstore = function (instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    var MyClass = instance.web.Class.extend({
        init: function (name) {
            this.name = name;
        },
        say_hello: function () {
            console.log("Hello", this.name);
        },
    });

    var MySpanishClass = MyClass.extend({
        say_hello: function () {
            var _super = this._super.bind(this);
            setTimeout(function () {
                _super();
            }.bind(this), 0);
            console.log("translation in Spanish: hola", this.name);
        },
    });

    local.HomePage = instance.Widget.extend({
        template: "HomePage",
        start: function () {
            return $.when(
                new local.PetToysList(this).appendTo(this.$('.oe_petstore_homepage_left')),
                new local.MessageOfTheDay(this).appendTo(this.$('.oe_petstore_homepage_right'))
            );
        }
    });

    local.MessageOfTheDay = instance.Widget.extend({
        template: 'MessageOfTheDay',
        start: function () {
            var self = this;
            return new instance.web.Model('oepetstore.message_of_the_day')
                .query(["message"])
                .order_by('-create_date', '-id')
                .first()
                .then(function (result) {
                    self.$(".oe_mywidget_message_of_the_day").text(result.message);
                });
        }
    });

    local.PetToysList = instance.Widget.extend({
        template: 'PetToysList',
        events: {
            'click .oe_petstore_pettoy': 'selected_item',
        },
        start: function () {
            var self = this;
            return new instance.web.Model('product.product')
                .query(['name', 'image'])
                .filter([['categ_id.name', '=', "Pet Toys"]])
                .limit(5)
                .all()
                .then(function (results) {
                    _(results).each(function (item) {
                        self.$el.append(QWeb.render('PetToy', {item: item}));
                    });
                });
        },
        selected_item: function (event) {
            this.do_action({
                type: 'ir.actions.act_window',
                res_model: 'product.product',
                res_id: $(event.currentTarget).data('id'),
                views: [[false, 'form']],
            });
        },
    });

    local.GreetingsWidget = instance.Widget.extend({
        className: 'oe_petstore_greetings',
        start: function () {
            this.$el.append("<div>Greeting to see you again in this menu.</div>");
        },
    });

    local.ProductsWidget = instance.Widget.extend({
        template: 'ProductsWidget',
        init: function (parent, products, color) {
            this._super(parent);
            this.products = products;
            this.color = color;
        },
    });

    local.ConfirmWidget = instance.Widget.extend({
        events: {
            'click button.ok_button': function () {
                this.trigger('user_chose', true);
            },
            'click button.cancel_button': function () {
                this.trigger('user_chose', false);
            }
        },
        start: function () {
            this.$el.append("<div>Are you sure you want to perform this action?</div>" +
                "<button class='ok_button btn btn-info'>OK</button>" +
                "<button class='cancel_button btn btn-danger'>Cancel</button>");

        },
    });

    local.ColorInputWidget = instance.Widget.extend({
        template: 'ColorInputWidget',
        events: {
            'change input': 'input_changed'
        },
        start: function () {
            this.input_changed();
            return this._super();
        },
        input_changed: function () {
            var color = [
                '#',
                this.$(".oe_color_red").val(),
                this.$('.oe_color_green').val(),
                this.$('.oe_color_blue').val()
            ].join('');
            this.set('color', color);
        },
    });

    instance.web.client_actions.add('petstore.homepage', 'instance.oepetstore.HomePage');


    instance.oepetstore.MessageListPage = instance.Widget.extend({
        template: 'message',
        init: function () {
            this._super.apply(this, arguments);
        },
        start: function () {
            var self = this;
            var records = new instance.web.Model('oepetstore.message_of_the_day');
            records.query(['message', 'create_date']).all().then(function (result) {
                self.$el.append($(QWeb.render('message_list', {msgList: result})));
                $('.button-view').click(function(e){
                    alert('View...');
                });
                $('.button-edit').click(function(e){
                    alert('edit...');
                });
                $('.button-cancel').click(function(e){
                    if (confirm('是否删除该记录?')) {
                        records.call('unlink', [parseInt($(this).attr('data'))]).then(function(){
                            window.location.reload();
                        });
                    }
                });
            });

        },
        // events: {
        //     'click .button-view': function () {
        //         alert('VIEW');
        //     },
        //     'click .button-edit': function () {
        //         alert('EDIT');
        //     },
        //     'click .button-cancel': 'my_cancel'
        // },
        // my_cancel: function () {
        //     alert('DELETE');
        // },
    });

    instance.web.client_actions.add('petstore.messagemenu', 'instance.oepetstore.MessageListPage');
    
    

    instance.oepetstore.ListView = instance.web.ListView.include({
        view_loading: function () {
            this._super.apply(this, arguments);
            $(".oe_list_content>thead>tr>th:first").css("width", "25px");
            $(".oe_list_content").colResizable({
                liveDrag: true,
                minWidth: 25,
            });
        }
    });

    instance.web.Dialog.include({
        open: function () {
            var self = this;
            this._super.apply(this, arguments);
            $('.modal.in').draggable({
                handle: '.modal-header'
            });
            return this;
        },
    });

    local.FieldChar2 = instance.web.form.AbstractField.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.set('value', '');
        },
        start: function () {
            this.on('change:effective_readonly', this, function () {
                this.display_field();
                this.render_value();
            });
            this.display_field();
            return this._super();
        },
        display_field: function () {
            var self = this;
            this.$el.html(QWeb.render("FieldChar2", {widget: this}));
            if (!this.get('effective_readonly')) {
                this.$('input').change(function () {
                    self.internal_set_value(self.$('input').val());
                });
            }
        },
        render_value: function () {
            if (this.get('effective_readonly')) {
                this.$el.text(this.get('value'));
            } else {
                this.$('input').val(this.get('value'));
            }
        },
    });

    local.FieldColor = instance.web.form.AbstractField.extend({
        events: {
            'change input': function (e) {
                if (!this.get('effective_readonly')) {
                    this.internal_set_value($(e.currentTarget).val());
                }
            },
        },
        init: function () {
            this._super.apply(this, arguments);
            this.set('value', '');
        },
        start: function () {
            this.on('change:effective_readonly', this, function(){
                this.display_field();
                this.render_value();
            });
            this.display_field();
            return this._super();
        },
        display_field: function(){
            this.$el.html(QWeb.render('FieldColor', {widget: this}));
        },
        render_value: function(){
            if (this.get('effective_readonly')) {
                this.$(".oe_field_color_content").css('background-color', this.get('value') || '#FFFFFF');
            } else {
                this.$('input').val(this.get('value') || '#ffffff');
            }
        },
    });

    instance.web.form.widgets.add('color', 'instance.oepetstore.FieldColor');
    instance.web.form.widgets.add('char2', 'instance.oepetstore.FieldChar2');

    // local.WidgetMultiplication = instance.web.form.FormWidget.extend({
    //     start: function(){
    //         this._super();
    //         this.field_manager.on("field_changed:integer_a", this, this.display_result);
    //         this.field_manager.on("field_changed:integer_b", this, this.display_result);
    //         this.display_result();
    //     },
    //     display_result: function(){
    //         var result = this.field_manager.get_field_value('integer_a') *
    //                      this.field_manager.get_field_value('integer_b');
    //         this.$el.text('a*b = '+result);
    //     },
    // });
    // instance.web.form.custom_widgets.add('multiplication', 'instance.web.WidgetMultiplication');
    //
    // local.WidgetCoordinates = instance.web.form.FormWidget.extend({
    //     events: {
    //         'click button': function () {
    //             navigator.geolocation.getCurrentPosition(
    //                 this.proxy('received_position'));
    //         }
    //     },
    //     start: function() {
    //         var sup = this._super();
    //         this.field_manager.on("field_changed:provider_latitude", this, this.display_map);
    //         this.field_manager.on("field_changed:provider_longitude", this, this.display_map);
    //         this.on("change:effective_readonly", this, this.display_map);
    //         this.display_map();
    //         return sup;
    //     },
    //     display_map: function() {
    //         this.$el.html(QWeb.render("WidgetCoordinates", {
    //             "latitude": this.field_manager.get_field_value("provider_latitude") || 0,
    //             "longitude": this.field_manager.get_field_value("provider_longitude") || 0,
    //         }));
    //         this.$("button").toggle(! this.get("effective_readonly"));
    //     },
    //     received_position: function(obj) {
    //         this.field_manager.set_values({
    //             "provider_latitude": obj.coords.latitude,
    //             "provider_longitude": obj.coords.longitude,
    //         });
    //     },
    // });
    //
    // instance.web.form.custom_widgets.add('coordinates', 'instance.oepetstore.WidgetCoordinates');
}


