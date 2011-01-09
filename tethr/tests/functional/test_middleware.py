from datetime import date, timedelta

from tethr.model import users, fixture_helpers as fh
from tethr.tests import *

class TestMiddleware(TestController):
    form_url = url_for(controller='test', action='rando_form')
    exception_url = url_for(controller='test', action='exception')
    
    def test_timer_proxy(self):
        u = fh.create_user()
        self.flush()
        self.login(u)
        
        response = self.post(self.form_url, {
            'a_number': 32,
            'a_string': 'aodij'
        })
        
        assert response.tmpl_context.show_debug == False
        assert response.tmpl_context.queries == ''
        
        u = fh.create_user(is_admin=True)
        self.flush()
        self.login(u)
        
        response = self.post(self.form_url, {
            'a_number': 32,
            'a_string': 'aodij'
        })
        
        assert response.tmpl_context.show_debug == True
        assert len(response.tmpl_context.queries) == 3
        assert response.tmpl_context.querie_time > 0.0
        
        for q, t in response.tmpl_context.queries:
            assert q
            assert t > 0.0
    
    """
    def test_error_middleware(self):
        u = fh.create_user()
        self.flush()
        self.login(u)
        
        response = self.client_async(self.exception_url, {
            'type': 'app'
        })
        
        assert 'debug' not in response
        
        u = fh.create_user(is_admin=True)
        self.flush()
        self.login(u)
        
        response = self.client_async(self.exception_url, {
            'type': 'app'
        })
        
        assert 'debug' in response
        assert response.debug
        assert response.debug.file
        assert response.debug.line
        assert response.debug.trace
        assert response.debug.url
        assert response.debug.message
    """