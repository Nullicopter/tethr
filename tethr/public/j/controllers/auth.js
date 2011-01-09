
;(function($){


Q.RegisterPage = Q.Page.extend({
    run: function(){
        this._super.apply(this, arguments);
        
        this.form = this.$('form').RedirectForm({
            defaultData: { default_timezone: -(new Date().getTimezoneOffset())/60 },
            resetInitially: true
        });
        this.form.focusFirst();
    }
});


})(jQuery);