
;(function($){
//

TESTS.test_base = function(){
    
    module('Base');
    
    var reload = $.reload;
    var redir = $.redirect;
    var P = PAGE.container;
    
    test('Reload Form', function(){
        expect(2)
        $.reload = function(){
            ok('reload was called');
        };
        
        var f = $('<form/>');
        P.append(f);
        
        var rf = new Q.ReloadForm(f, {
            onSuccess: function(){
                ok('My call back was called!');
            }
        });
        
        rf._onSuccess({});
        $.reload = reload;
    });
    
    test('Redirect Form', function(){
        expect(3)
        $.redirect = function(url, h){
            equals(url, '/omgwow/yeah');
            equals(h, undefined);
        };
        
        var f = $('<form/>');
        P.append(f);
        
        var rf = new Q.RedirectForm(f, {
            onSuccess: function(){
                ok('My callback was called!');
            }
        });
        
        rf._onSuccess({results: {url: '/omgwow/yeah'}});
        $.redirect = redir;
    });
    
};

//
})(jQuery);