from tethr.lib.base import *
from pylons.controllers.util import abort

import sys
import time
import simplejson
import sqlalchemy as sa
from datetime import datetime

from pylons_common.controllers import ApiMixin

VALIDATION_ERROR_RESPONSE_CODE = 400
API_MODULE_BASE = 'tethr.api'
API_SIGNATURE_BASE = 'tethr.controllers.api'

#this is the Current version of the API.
API_VERSION = 1
API_ARGS = {
    'controller': 'api',
    'version': API_VERSION,
    'action': 'dispatch'
}

class ApiController(BaseController, ApiMixin):
    
    # for the api mixin
    Session = Session
    API_MODULE_BASE = API_MODULE_BASE
    API_SIGNATURE_BASE = API_SIGNATURE_BASE
    
    def authenticate(self):
        """
        Authenticate the user before proceeding with the API call.
        """        
        user = None
        real_user = None
        auth_type = None
        
        if request.headers.get('Authenticate') or request.headers.get('Authorization'):

            auth_type = u'http'
            
            # Artlessly smash beaker sessions so we don't waste header space on the adroll cookie.
            request.environ['beaker.session'].__dict__['_headers']['cookie_out'] = ''
            
            # Sign user in using basic HTTP auth
            user = auth.authenticate_basic_auth()
            real_user = user
            if user:
                logger.info("%s logged in with basic HTTP authentication" % user)
            else:
                raise ApiPrologueException(403, "Login credentials denied", errors.FORBIDDEN)
        else:
            auth_type = u'cookie'
            
            user = auth.get_user()
            real_user = auth.get_real_user()
            logger.info('%s logged in with session cookie' % (user))
        
        return user, real_user, auth_type
