from tethr.lib.base import *
from tethr.model import users

import formencode
import formencode.validators as fv

import sqlalchemy as sa

class UniqueEmail(fv.FancyValidator):
    def _to_python(self, value, state):
        # we don't support multiple values, so we run a quick check here (we got a webapp where this was a problem)
        if type(value) != type(u""):
            raise fv.Invalid('You must supply a valid email.', value, state)
        
        user = Session.query(users.User).filter(sa.func.lower(users.User.email)==value.lower()).first()
        # if this user is the same as the logged in one then don't throw the error - allows keeping old email address when editing contact info
        if user and user != auth.get_user():
            raise fv.Invalid('That user already exists. Please choose another.', value, state)
        return value

class RegisterForm(formencode.Schema):
    
    password = fv.UnicodeString(not_empty=True, min=5, max=32)
    confirm_password = fv.UnicodeString(not_empty=True, min=5, max=32)
    email = formencode.All(fv.Email(not_empty=True), fv.MaxLength(64), UniqueEmail())
    default_timezone = fv.Int(not_empty=True)
    
    chained_validators = [fv.FieldsMatch('password', 'confirm_password')]

class LoginForm(formencode.Schema):
    username = formencode.All(fv.UnicodeString(not_empty=True), fv.MaxLength(64))
    password = formencode.All(fv.UnicodeString(not_empty=True), fv.MaxLength(32))

class AuthController(BaseController):
    """
    """
    
    @dispatch_on(POST='_do_login')
    def login(self):
        c.title = 'Login!'
        
        if auth.is_logged_in():
            self.redirect('/')
        
        return self.render('/auth/login.html');
    
    @mixed_response('login')
    def _do_login(self, **kw):
        
        scrubbed = self.validate(LoginForm, **dict(request.params))
        
        url = auth.authenticate(**scrubbed)
        
        self.commit()
        return {'url': url or '/'}
    
    @dispatch_on(POST='_do_register')
    def register(self):
        c.title = 'Register'
        
        if auth.is_logged_in():
            self.redirect('/')
        
        return self.render('/auth/register.html');
    
    @mixed_response('register')
    def _do_register(self, **kw):
        
        numusers = len(Session.query(users.User).all())
        
        scrubbed = self.validate(RegisterForm, **dict(request.params))
        
        user = users.User()
        self.add(user)
        
        user.email = scrubbed.email
        user.username = scrubbed.email
        user.password = scrubbed.password
        user.set_timezone_int(scrubbed.default_timezone)
        
        #first user is an admin. 
        if numusers == 0:
            user.role = users.ROLE_ADMIN
        
        self.commit()
        
        return {'url': auth.login(user) or '/'}
    
    
    def logout(self):
        auth.logout()
        
        return self.redirect('/')

