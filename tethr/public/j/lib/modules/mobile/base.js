
;(function($){

//tethrs

Q.Profile = Q.Model.extend({
    urls: {
        'create': '/api/v1/profile/teather',
        'update': '/api/v1/profile/add_data'
    },
    
    init: function(model, settings){
        model.id = model.eid;
        
        this._super.apply(this, arguments);
    },
    
    parse: function(data){
        $.log('Parsing profile success', data.results);
        return data.results;
    },
    
    toJSON: function(method){
        return $.extend({
            profile: this.get('eid')
        }, this.get('data') || {});
    },
    
    getData: function(){
        var data = this.get('data');
        if(data){
            data = _.clone(data);
            if('name' in data)
                delete data['name'];
        }
        
        return data;
    },
    
    getSortKey: function(){
        var name = this.getName();
        var key = null;
        if(name){
            name = name.trimsplit(' ');
            if(name.length > 1)
                key = name.slice(1).join(' ');
            else if(name == 1)
                key = name[0];
        }
        return key;
    },
    
    getName: function(){
        var name = this.get('name');
        var data = this.get('data');
        if(!name)
            name = data['name'];
        
        if(!name) 
            $.warn('No name!', m);
        
        return name;
    }
});

Q.Profiles = Q.Collection.extend({
    
    model: Q.Profile,
    
    comparator: function(profile) {
        return profile.getSortKey();
    },
    
    init: function(models, settings){
        this._super.apply(this, arguments);
        _.bindAll(this, 'fetchForVersion');
    },
    
    _add: function(m, options){
        options = options || {};
        var model = this._super.call(this, m, options);
        
        $.log('Adding profile', model.isNew() ? 'NEW' : 'NOT new', m, options);
        
        if(model.isNew())
            if(options.silent != true)
                model.save();
    },
    
    addTether: function(profileDict, options){
        $.log('Adding new profile: ', profileDict);
        this.add({data: profileDict}, options);
    }
});

})(jQuery);