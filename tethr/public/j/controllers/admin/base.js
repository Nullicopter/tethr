
;(function($){


$(document).ready(function(){
    //Make all the sections collapsable.
    /*$('.inspect-section').each(function(){
        var sect = $(this);
        var link = $('<a/>', {href: '#', text: 'hide', style: 'font-size: 8pt;'});
        sect.find('h3').append($('<span/>', {text: '  '}));
        sect.find('h3').append(link);
        var tog = sect.find('>:not(h3)');
        
        link.toggler({
            initiallyHidden: sect.hasClass('hide'),
            linkText: {opened: 'hide', closed: 'show'},
            toToggle: tog
        });
    });*/
    
    $('.reload-form').ReloadForm();
    $('.reload-link').reloadLink();
    
    $('.editable').each(function(){
        var t = $(this);
        t.find('span').EditableField({
            editLink: t.find('.edit-link'),
            hoverShowContainer: '.attribute-table'
        });
    });
});


})(jQuery);