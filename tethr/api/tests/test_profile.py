from tethr.api import authorize, enforce, FieldEditor, convert_date
from tethr.model import fixture_helpers as fh, Session, users, profiles, data
from tethr import api
from tethr.tests import *

from datetime import datetime, timedelta

import formencode
import formencode.validators as fv

from pylons_common.lib.exceptions import *

class TestProfile(TestController):
    
    def test_get(self):
        u = fh.create_user()
        
        profile = fh.create_profile(email=u'meow+yeahman@omg.com')
        self.flush()
        
        pro = api.profile.get(u,u, profile=profile.eid)
        assert pro == profile
        
        pro = api.profile.get(u,u, email=u'meow@omg.com')
        assert pro == profile
    
    def test_teather(self):
        u = fh.create_user()
        
        p1 = fh.create_profile(email=u'meow+yeahman@omg.com')
        p2 = fh.create_profile(email=u'heyman@wowza.com')
        self.flush()
        
        k = {
            'notes': u'I met this guy here and there.',
            'phone:work': u'510-234-1245',
            'phone:home': u'510-234-2341'
        }
        profile = api.profile.teather(p1.user, p1.user, email=u'heyman@wowza.com', **k)
        self.flush()
        
        assert p2 == profile
        
        phone = data.PhoneHandler()
        d = p2.fetch_data(user=p1.user)
        assert len(d) == 5 # name, phone*2, notes, email
        for dp in d:
            if dp.key == 'notes': assert dp.value == k['notes']
            if dp.key == 'phone' and dp.type == 'work': assert dp.value == phone.normalize(k['phone:work'])
            if dp.key == 'phone' and dp.type == 'home': assert dp.value == phone.normalize(k['phone:home'])
        
        
        profile = api.profile.teather(p1.user, p1.user, email=u'unclaimed@poo.com', name=u'Some Guy')
        assert profile
        
        dps = profile.fetch_data(user=p1.user)
        print dps
        d = dict([(p.key, p.value) for p in dps])
        assert 'name' in d
        assert 'email' in d
        