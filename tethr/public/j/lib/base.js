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

$.extend($, {
    relativeDate: function(date, now){
        now = now || new Date();
        
        ret = {};
        ret.mstotal = date - now; //12345678
        ret.ispast = ret.mstotal < 0;
        ret.mstotal = Math.abs(ret.mstotal);
        
        ret.ms = ret.mstotal % 1000; //678 ms
        ret.sectotal = parseInt(ret.mstotal/1000); //12345
        ret.sec = ret.sectotal%60; //45 sec
        ret.mintotal = parseInt(ret.sectotal/60); //205 min
        ret.min = ret.mintotal%60; //25 min
        ret.hourstotal = parseInt(ret.mintotal/60); //3 hours
        ret.hours = ret.hourstotal%24; //3 hours
        ret.daystotal = parseInt(ret.hourstotal/24); //0 days
        
        return ret;
    },
    
    relativeDateStr: function(date, now){
        now = now || new Date();
        
        if(!date) return 'unknown';
        
        data = $.relativeDate(date, now);
        $.log(data);
        
        if(data.sectotal < 10 && data.ispast) return 'Just now';
        
        if(data.daystotal > 7) return $.formatDate(date, "b e, Y");
        
        function modret(str){
            if(data.ispast)
                return str + ' ago';
            return 'in ' + str;
        }
        
        if(data.daystotal == 1 && data.ispast)
            return 'Yesterday'
        if(data.daystotal == 1 && !data.ispast)
            return 'Tomorrow'
        
        if(data.daystotal > 0)
            return modret($.pluralize(data.daystotal, '{0} days', '{0} day'));
        
        if(data.hourstotal)
            return modret($.pluralize(data.hourstotal, '{0} hours', '{0} hour'));
        
        if(data.mintotal)
            return modret($.pluralize(data.mintotal, '{0} minutes', '{0} minute'));
        
        if(data.sectotal)
            return modret($.pluralize(data.sectotal, '{0} seconds', '{0} second'));
        
        if(data.mstotal)
            return modret($.pluralize(data.mstotal, '{0} millis', 'now!'));
        
        return $.formatDate(date, "b e, Y");
    }
});

$(document).ready(function(){
    $('.reload-link').reloadLink();
});

})(jQuery);


