from tethr.api import authorize, enforce, FieldEditor, convert_date
from tethr.model import fixture_helpers as fh, Session, users, profiles
from tethr import api
from tethr.tests import *

from datetime import datetime, timedelta

import formencode
import formencode.validators as fv

from pylons_common.lib.exceptions import *

class TestUser(TestController):
    
    def test_set_pref(self, admin=False):
        pass
    
    def test_create(self):
        user = api.user.create(name=u"Jim Bob", email=u'aoijd+yeahman@omg.com', password=u'concon',
                               confirm_password=u'concon', default_timezone=u'-8')
        self.flush()
        
        assert user.profile
        
        keys = {
            'name': u'Jim Bob',
            'email': u'aoijd@omg.com'
        }
        for dp in user.profile.data_points:
            assert dp.value == keys[dp.key]
    
    def test_create_unclaimed(self):
        
        #unclaimed profile!
        profile = fh.create_profile(user=None, email=u'aoijd+yeahman@omg.com')
        profile.add_data(fh.create_user(), 'email', u'aoijd+yeahman@omg.com')
        self.flush()
        l = len(Session.query(profiles.Profile).all())
        uncl = profiles.Profile.find_unclaimed(u'aoijd@omg.com')
        assert uncl
        
        user = api.user.create(name=u"Jim Bob", email=u'aoijd@omg.com', password=u'concon',
                               confirm_password=u'concon', default_timezone=u'-8')
        self.flush()
        
        # did not create a new one!
        assert l == len(Session.query(profiles.Profile).all())
        assert user.profile.id == profile.id
        
        uncl = profiles.Profile.find_unclaimed(u'aoijd@omg.com')
        assert not uncl
        
        user.profile.add_data(user, 'email', 'something@else.com')
        self.flush()
        
        # new users cannot use these email addresses.
        assert 'email' in self.throws_exception(lambda: api.user.create(name=u"jads", email=u'something@else.com', password=u'concon',
                               confirm_password=u'concon', default_timezone=u'-8')).error_dict
        assert 'email' in self.throws_exception(lambda: api.user.create(name=u"jasd", email=u'aoijd@omg.com', password=u'concon',
                               confirm_password=u'concon', default_timezone=u'-8')).error_dict
    
    def test_edit(self):
        own = fh.create_user()
        rando = fh.create_user()
        a = fh.create_user(is_admin=True)
        self.flush()
        
        u = api.user.edit(own, own, own, first_name='omgwow', default_timezone=0, is_active='f', role='admin')
        
        assert u.id == own.id
        assert u.first_name == 'omgwow'
        assert u.is_active == True
        assert u.role == 'user'
        assert 'London' in u.default_timezone
        
        u = api.user.edit(a, a, own, last_name='yeah')
        assert u.id == own.id
        
        u = api.user.edit(a, a, own, is_active='f', role='admin')
        assert u.id == own.id
        assert u.is_active == False
        assert u.role == 'admin'
        
        assert self.throws_exception(lambda: api.user.edit(rando, rando, own, first_name='m')).code == NOT_FOUND
        assert self.throws_exception(lambda: api.user.edit(a, a, None, first_name='s')).code == NOT_FOUND   

