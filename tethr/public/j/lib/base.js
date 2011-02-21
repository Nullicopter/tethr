;/*******************************************************************************
 *
 ******************************************************************************/

(function($){


//Overrides
Q.Loader.defaults.image = '/i/loaders/16x16_arrows.gif';
Q.AsyncForm.defaults.autoGenValidationOptions = true;

//Mustache-like delimiters!
_.templateSettings = {
  interpolate : /\{\{(.+?)\}\}/g
};

// This is the fastest trim out there, apparently:
// http://blog.stevenlevithan.com/archives/faster-trim-javascript
String.prototype.trim = function() {
    var str = this;
	str = str.replace(/^\s+/, '');
	for (var i = str.length - 1; i >= 0; i--) {
		if (/\S/.test(str.charAt(i))) {
			str = str.substring(0, i + 1);
			break;
		}
	}
	return str;
}

String.prototype.trimsplit = function(){
    var arr = this.trim().split.apply(this, arguments);
    var newarr = [];
    for(var i = 0; i < arr.length; i++){
        if(arr[i].length > 0)
            newarr.push(arr[i]);
    }
    return newarr;
};

Q.defaultValidationOptions = {
    errorPlacement: function(error, element) {
        var errc = $('<div class="error-container"></div>');
        
        errc.append(error);
        
        element.parent().append(errc);
    },
    success: function(element){
    }
};

Q.Page = Q.Module.extend({
    pageId:'#page',
    
    init: function(settings){
        this.args = arguments;
        this.settings = settings;
        window.PAGE = this;
    },
    
    readyrun: function(){
        var self = this;
        var args = arguments;
        $(document).ready(function(){
            self.run.apply(self, args);
        });
    },
    
    run: function(){
        this.container = $(this.pageId);
        this.delegateEvents();
        this.cacheNodes();
    }
});

Q.RedirectForm = Q.AsyncForm.extend('RedirectForm', {
    _onSuccess: function(data){
        this._super.apply(this, arguments);
        
        if(data && data.results && data.results.url)
            $.redirect(data.results.url);
    }
});

Q.ReloadForm = Q.AsyncForm.extend('ReloadForm', {
    _onSuccess: function(data){
        this._super.apply(this, arguments);
        $.reload();
    }
});

$.fn.reloadLink = function(){
    this.click(function(){
        $.post(this.href, {}, function(){
            $.reload();
        });
        return false;
    });
};

$(document).ready(function(){
    $('.reload-link').reloadLink();
});

})(jQuery);


