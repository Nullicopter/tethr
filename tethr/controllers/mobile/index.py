from tethr.lib.base import *
from tethr import api
from tethr.controllers.api import v1

class IndexController(BaseController):
    """
    """
    def __before__(self):
        c.real_user = auth.get_real_user()
        c.user = auth.get_real_user()
        if not c.real_user:
            self.redirect(h.url_for(controller='mobile/auth', action='login'))
    
    def index(self):
        serial = v1.profile.get(c.real_user, c.user)
        c.profiles = serial.output(api.profile.get(c.real_user, c.user))
        
        return self.render('/mobile/index.html')

