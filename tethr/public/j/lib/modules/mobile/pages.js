
;(function($){

Q.MobilePage = Q.Page.extend({
    pageId: 'body'
});

Q.RegisterPage = Q.MobilePage.extend({
    run: function(){
        this._super.apply(this, arguments);
        
        this.form = this.$('form').RedirectForm({
            defaultData: { default_timezone: -(new Date().getTimezoneOffset())/60 },
            resetInitially: true
        });
        this.form.focusFirst();
    }
});

Q.LoginPage = Q.MobilePage.extend({
    run: function(){
        this._super.apply(this, arguments);
        
        this.form = this.$('form').RedirectForm({});
        this.form.focusFirst();
    }
});

//TODO: there is a disconnect between the request and which form made that request
//we need to fix this if the server validation push is to work...

/***
 * Saving a guy
 */

Q.AddContactPage = Q.Module.extend('AddContactPage',{
    n: {
        header: '.header h1',
        cancel: '.cancel'
    },
    events: {
        'click .save-button': 'clickSaveButton'
    },
    
    init: function(container, settings){
        this._super(container, settings);
        _.bindAll(this, 'formSubmit', 'onSuccess', 'onFail', 'onPageBeforeShow');
        
        var self = this;
        var form = this.$('form');
        
        this.form = form.Form({
            validationOptions: {
                rules: {name: 'required', email: 'required'},
                submitHandler: this.formSubmit
            }
        });
        
        this.settings.profiles.bind('request:start', function(){$.mobile.pageLoading()});
        this.settings.profiles.bind('request:end', this.onRequestEnd);
        
        this.container.bind('pagebeforeshow', this.onPageBeforeShow);
        
        //save the last thing we entered into the notes field
        this.lastNotes = '';
    },
    
    clickSaveButton: function(){
        this.form.submit();
    },
    
    onPageBeforeShow: function(){
        var profile = this.settings.current.get('profile');
        if(profile){
            this.n.header.text('Edit');
            var data = profile.getData();
            var name = profile.getName();
            
            this.form.reset();
            this.form.load($.extend({}, data, {
                name: name
            }));
            
            this.n.cancel[0].href = '#view';
        }
        else{
            this.n.header.text('Add');
            this.form.reset();
            this.form.load({notes:this.lastNotes});
            this.n.cancel[0].href = '#listview';
        }
        this.form.focusFirst();
    },
    
    onRequestEnd: function(err, args){
        $.log('request:end', err, args);
        $.mobile.pageLoading(true);
    },
    
    formSubmit: function(e){
        var self = this;
        var profile = this.settings.current.get('profile');
        var val = this.form.val();
        this.lastNotes = val.notes || '';
        if(profile){
            profile.save({
                data: val
            }, {
                success: function(){
                    self.trigger('editedprofile', profile);
                }
            });
        }
        else
            this.settings.profiles.addTether(val);
        
        return false;
    }
});

/***
 * Viewing a list of guys
 */

Q.ListContactsPage = Q.View.extend('ListContactsPage', {
    tag: 'div',
    
    template: '#list-template',
    dividerTemplate: '#list-divider-template',
    itemTemplate: '#list-item-template',
    letters: ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'],
    
    events: {
        'click .profile': 'clickProfile'
    },
    
    n:{content: '.content'},
    
    init: function(container, settings){
        this._super(container, settings);
        _.bindAll(this, 'onAddProfile', 'onUpdateProfile', 'onRemoveProfile')
        var self = this;
        
        self.template = $(this.template);
        self.dividerTemplate = $(this.dividerTemplate);
        self.itemTemplate = $(this.itemTemplate);
        
        self.settings.profiles.bind('add', this.onAddProfile);
        self.settings.profiles.bind('remove', this.onRemoveProfile);
        self.settings.profiles.bind('change', this.onUpdateProfile);
        
        //de select the current profile when they view this page.
        self.container.bind('pagebeforeshow', function(){self.settings.current.set({profile:null}, {silent:true})});
        
        self.render();
    },
    
    render: function(){
        this.n.content.html(_.template(this.template.html(), {}));
        
        this.list = this.$('ul');
        var div = this.dividerTemplate.html();
        
        for(var i = 0; i < this.letters.length; i++){
            this.list.append(_.template(div, {
                id: this.letters[i],
                letter: this.letters[i]
            }));
        }
        
        //add all the peeps
        
        this.list.listview();
        this.list.find('.list-divider').hide();
    },
    
    refresh: function(){
        
        this.list.listview('refresh');
    },
    
    hideEmptyItems: function(){
        this.$('.list-divider').each(function(){
            var t = $(this);
            if(!t.next().is('.list-item'))
                t.hide();
        });
    },
    
    clickProfile: function(e){
        var targ = $(e.target);
        var eid = targ.attr('rel');
        if(eid)
            this.settings.current.set({
                profile: this.settings.profiles.get(eid)
            });
    },
    
    onUpdateProfile: function(m){
        $.log('updating profile!', m);
        var item = this.list.find('#'+m.cid);
        item.remove();
        this.onAddProfile(m, m.collection);
        this.hideEmptyItems();
    },
    
    onRemoveProfile: function(m){
        $.log('Removing profile....', m);
        var item = this.list.find('#'+m.cid);
        item.remove();
        this.hideEmptyItems();
    },
    
    onAddProfile: function(m, coll){
        var name = m.getName();
        
        var letter = m.getSortKey()[0].toUpperCase();
        var letterObj = this.$('.'+letter + ':last');
        
        var item = $(_.template(this.itemTemplate.html(), {
            name: name,
            eid: m.get('eid') || '',
            letter: letter,
            id: m.cid
        }));
        
        if(letterObj.length)
            item.insertAfter(letterObj);
        else{
            letterObj = this.$('#'+letter);
            item.insertAfter(letterObj);
            letterObj.show();
        }
        
        $.log('showing', name, m, letter, letterObj, this.$('#'+letter));
        
        if(!m.isNew())
            this.refresh();
    }
});

/***
 * Viewing a guy
 */

Q.DataFormatters.email = function(v){
    return $.replace('<a href="mailto:{0}">{0}</a>', [v]);
};

Q.DataFormatters.phone = function(v){
    return $.replace('<a href="tel:{0}">{0}</a>', [v]);
};

Q.ViewContactPage = Q.View.extend('ViewContactPage', {
    template: '#view-detail-template',
    dataTemplate: '#data-point-template',
    
    n:{content: '.content'},

    init: function(container, settings){
        this._super(container, settings);
        _.bindAll(this, 'onPageBeforeShow');
        
        this.container.bind('pagebeforeshow', this.onPageBeforeShow);
        
        this.template = $(this.template).html();
        this.dataTemplate = $(this.dataTemplate).html();
    },
    
    onPageBeforeShow: function(){
        $.log('showing', this.settings.current);
        this.render();
    },
    
    render: function(){
        var profile = this.settings.current.get('profile');
        if(!profile)
            return this;
        
        var name = profile.getName();
        
        this.n.content.html(_.template(this.template, {
            url: profile.get('url'),
            name: name
        }));
        
        this.data = this.$('.display-data');
        var data = profile.getData();
        
        for(var k in data){
            var d = k.trimsplit(':');
            var p = {
                value: Q.DataFormatters.get(k, data[k]),
                key: d[0],
                type: d.length > 1 ? d[1] : ''
            };
            this.data.append(_.template(this.dataTemplate, p));
        }
        
        return this;
    }
});

/***
 * Putting it all together
 */

Q.IndexPage = Q.MobilePage.extend({
    run: function(){
        this._super.apply(this, arguments);
        _.bindAll(this, 'onAddNewProfile', 'onViewProfile', 'onEditedProfile');
        
        this.profiles = new Q.Profiles([]);
        this.current = new Backbone.Model({});
        
        var params = {
            profiles: this.profiles,
            current: this.current
        };
        
        //bind to the models here
        
        //a change in eid indicates an update from the server.
        this.profiles.bind('change:eid', this.onAddNewProfile);
        this.current.bind('change:profile', this.onViewProfile);
        
        this.addPage = this.$('#add').AddContactPage(params);
        this.listPage = this.$('#listview').ListContactsPage(params);
        this.viewPage = this.$('#view').ViewContactPage(params);
        
        this.addPage.bind('editedprofile', this.onEditedProfile);
        
        this.profiles.add(this.settings.profiles);
        
        this.listPage.refresh();
        
        var active = $.mobile.activePage;
        $.log(active);
        if(active[0].id != this.listPage.container[0].id)
            $.mobile.changePage(this.listPage.container);
    },
    
    onEditedProfile: function(m){
        $.log('Edited profile', m);
        this.current.set({profile: m});
        this.viewPage.render();
        $.mobile.changePage(this.viewPage.container);
    },
    
    onAddNewProfile: function(m){
        $.log('Got new profile', m);
        this.current.set({profile: m});
    },
    
    onViewProfile: function(m){
        $.mobile.changePage(this.viewPage.container);
    }
    
});


})(jQuery);