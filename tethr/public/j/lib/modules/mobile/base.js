
;(function($){

//tethrs

Q.Profile = Q.Model.extend({
    urls: {
        'create': '/api/v1/profile/teather',
        'update': '/api/v1/profile/add_data'
    },
    
    nameMap: {
        email: 'Email',
        tags: 'Tags',
        notes: 'Notes'
    },
    
    sortKeys: {
        email: 1,
        tags: 2,
        notes: 3
    },
    
    datasortFn: function(left, right){
        lnum = this.sortKeys[left];
        rnum = this.sortKeys[right];
        
        //the ones in sortKeys come first!
        if(lnum && rnum) return lnum - rnum;
        if(lnum) return -lnum;
        if(rnum) return rnum;
        
        if(left > right)
            return 3;
        else if (left < right)
            return -3;
        
        return 0;
    },
    
    init: function(model, settings){
        model.id = model.eid;
        _.bindAll(this, 'datasortFn');
        
        this._super.apply(this, arguments);
    },
    
    parse: function(data){
        if(this.collection && this.isNew()){
            $.log('Removing Duplicate', this.collection, data.results.id);
            this.collection.remove(data.results.id);
        }
        
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
            //data = _.clone(data);
            var keys = [];
            for(var k in data)
                keys.push(k);
            keys.sort(this.datasortFn);
            $.log(keys);
            
            var d = {};
            for(var i = 0; i < keys.length; i++)
                if(keys[i] != 'name')
                d[keys[i]] = data[keys[i]];
            data = d;
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
        //var s = profile.get('created_date') ? -$.parseDate(profile.get('created_date')).getTime() : Number.MIN_VALUE;
        //$.log(profile.getName(), s);
        //return profile.getSortKey();
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