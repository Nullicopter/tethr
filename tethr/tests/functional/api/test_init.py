from datetime import date, timedelta

from tethr.model import users, fixture_helpers as fh
from tethr.tests import *

from pylons_common.lib.exceptions import *

class TestInit(TestController):
    
    url = api_url('error', 'explode')
    
    def test_api_prologue_exception(self):
        """
        Verifies that an ApiPrologueException is handled properly
        """
        user = fh.create_user()
        self.flush()
        
        self.login(user)
        
        # The bad version in this url will force an ApiPrologueException in the dispatcher
        bad_url = '/api/vA/user/set_pref'
        params = {'key': 'asd', 'value': 'omgwow'}
        
        response = self.client_async(bad_url, params, status=501, assert_success=False)
        assert 'Invalid version' in response.results.errors[0].message
        
        # no function!
        url = '/api/v1/user/meow'
        params = {}
        response = self.client_async(url, params, status=501, assert_success=False)
        assert 'user.meow not implemented' in response.results.errors[0].message
        
        # no module!
        url = '/api/v1/rawr/meow'
        params = {}
        response = self.client_async(url, params, status=501, assert_success=False)
        assert 'rawr.meow not implemented' in response.results.errors[0].message

    def test_value_error(self):
        """
        Verifies that a ValueError is handled properly
        """
        # we cant create a new user because of the rollback when there is an error.
        user = fh.create_user(is_admin=True)
        self.flush()
        
        self.login(user)
        
        # Force a ValueError with a bad budget value
        params = {'anint': 'not an int'}
        response = self.client_async(self.url, params, status=500, assert_success=False)
        assert 'int()' in response.results.errors[0].message
    
    def test_not_logged_in_error(self):
        """
        Verifies that a ValueError is handled properly
        """
        params = {}
        response = self.client_async(self.url, params, status=400, assert_success=False)
    
    def test_bool(self):
        u2 = fh.create_user(is_admin=True)
        self.flush()
        self.login(u2)
        
        r = self.client_async(self.url,{'abool': 'on'})
        assert r.results.abool == True
    
    def test_auth(self):
        
        # not an admin
        u = fh.create_user()
        self.flush()
        self.login(u)
        
        r = self.client_async(self.url,{}, status=403, assert_success=False)
        assert r.errors[0].code == FORBIDDEN
        