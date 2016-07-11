openerp.yycrm = function(instance, local){
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    // 实现弹出窗口可拖动
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

    // console.log(require('sales_team.dashboard'));
    // var SalesTeamDashboardView = instance.sales_team.dashboard;
    // console.log(SalesTeamDashboardView);
};