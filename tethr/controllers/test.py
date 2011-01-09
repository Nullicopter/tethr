from tethr.lib.base import *
from tethr.model import users
from tethr import api

from pylons_common.lib.exceptions import *

import formencode
import formencode.validators as fv

class TestController(BaseController):
    """
    A controller that has middleware exercise actions.
    """
    
    def qunit(self):
        return self.render('/test/qunit.html');
    
    def exercise(self):
        return self.render('test/exercise.html');
    
    @ajax
    def rando_form(self, **_):
        """
        A dumb form handler that makes two queries.
        
        The middleware tests use this, so be careful changing.
        """
        
        class RandoForm(formencode.Schema):
            a_number = fv.Int(not_empty=True)
            a_string = formencode.All(fv.UnicodeString(not_empty=True), fv.MaxLength(20))
        
        scrubbed = self.validate(RandoForm, **dict(request.params))
        
        #useless queries
        Session.query(users.User).all()
        Session.query(users.User).all()
        
        Session.query(users.UserPreference).filter_by(user_id=1).all()
        
        return dict(scrubbed)
    