from tethr.lib.base import *
from tethr.model import users
from tethr import api

import formencode
import formencode.validators as fv

import sqlalchemy as sa

class LoginForm(formencode.Schema):
    username = formencode.All(fv.UnicodeString(not_empty=True), fv.MaxLength(64))
    password = formencode.All(fv.UnicodeString(not_empty=True), fv.MaxLength(32))

class AuthController(BaseController):
    """
    """
    
    @dispatch_on(POST='_do_login')
    def login(self):
        c.title = 'Login'
        
        if auth.is_logged_in():
            self.redirect('/')
        
        return self.render('/mobile/login.html');
    
    @mixed_response('login')
    def _do_login(self, **kw):
        
        scrubbed = self.validate(LoginForm, **dict(request.params))
        
        url = auth.authenticate(**scrubbed)
        
        self.commit()
        return {'url': h.url_for(controller='mobile/index', action='index')}
    
    @dispatch_on(POST='_do_register')
    def register(self):
        c.title = 'Register'
        
        if auth.is_logged_in():
            self.redirect('/')
        
        return self.render('/mobile/register.html');
    
    @mixed_response('register')
    def _do_register(self, **kw):
        
        user = api.user.create(**dict(request.params))
        
        self.commit()
        
        return {'url': h.url_for(controller='mobile/index', action='index')}
    
    
    def logout(self):
        auth.logout()
        
        return self.redirect(h.url_for(controller='mobile/index', action='index'))

