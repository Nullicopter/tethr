
;(function($){
    
    window.TESTS = {};

    Q.TestPage = Q.Page.extend({
        run: function(args){
            this._super();
            for(var test in TESTS){
                $.log('Running "', test, '"...');
                TESTS[test](args);
            }
        }
    });

})(jQuery);