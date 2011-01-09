from tethr.api import authorize, enforce, FieldEditor, convert_date
from tethr.model import fixture_helpers as fh, Session, users
from tethr import api
from tethr.tests import *

from datetime import datetime, timedelta

import formencode
import formencode.validators as fv

from pylons_common.lib.exceptions import *

class TestUser(TestController):
    
    def test_set_pref(self, admin=False):
        pass
    
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

