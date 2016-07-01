openerp.oepetstore = function(instance, local) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    local.HomePage = instance.Widget.extend({
        start: function() {
            console.log("pet store home page loaded");
        },
    });

    instance.web.client_actions.add('petstore.homepage', 'instance.oepetstore.HomePage');


    instance.oepetstore.MessageListPage = instance.Widget.extend({
        template: 'message',
        init: function(){
            this._super.apply(this, arguments);
        },
        start: function(){
            var self = this;
            new instance.web.Model('oepetstore.message_of_the_day').query(['message','create_date']).all().then(function(result){
                var ss = result.message + result.create_date;
                self.$el.append($(QWeb.render('message_list', {msgList: result})));
                $('.button-view').click(function(e){
                    alert('View...');
                });
                $('.button-edit').click(function(e){
                    alert('edit...');
                });
                $('.button-cancel').click(function(e){
                    alert('cancel...');
                });
            });
        },
    });

    instance.web.client_actions.add('petstore.messagemenu', 'instance.oepetstore.MessageListPage');

    instance.oepetstore.ListView = instance.web.ListView.include({
        view_loading: function() {
            this._super.apply(this, arguments);
            $(".oe_list_content>thead>tr>th:first").css("width","25px");
            $(".oe_list_content").colResizable({
                 liveDrag:true,
                 minWidth:25,
            });
        }
    });
}


