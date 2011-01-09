
from tethr.lib.base import BaseController, h, c, auth, abort, redirect

class AdminController(BaseController):
    
    def __before__(self, *a, **kw):
        if not auth.is_admin():
            return redirect('/')
            #abort(404)