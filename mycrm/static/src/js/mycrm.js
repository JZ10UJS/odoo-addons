openerp.mycrm = function(instance, local){
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
};