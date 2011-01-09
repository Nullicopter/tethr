from tethr.api import enforce, logger, validate, h, authorize, \
                    AppException, ClientException, CompoundException, \
                    INVALID, NOT_FOUND, FORBIDDEN, abort, FieldEditor, auth

from tethr.model import users
import sqlalchemy as sa

import formencode
import formencode.validators as fv

ID_PARAM = 'u'

ROLES = [users.ROLE_USER, users.ROLE_ADMIN, users.ROLE_ENGINEER]
EDIT_FIELDS = ['password', 'first_name', 'last_name', 'default_timezone']
ADMIN_EDIT_FIELDS = ['role', 'is_active', 'username']

@enforce(key=unicode, value=unicode, use_real_user=bool)
def set_pref(real_user, user, key, value, use_real_user=True):
    
    class Pref(formencode.Schema):
        key     = fv.MaxLength(64, not_empty=True)
        value   = fv.MaxLength(64, not_empty=False)
    scrubbed = validate(Pref, key=key, value=value)
    
    u = user
    if use_real_user:
        u = real_user
    u.set_preference(scrubbed.key, scrubbed.value or '')

def generate_password():
    return utils.uuid()[:8]

@enforce(id=users.User)
@authorize(check_admin=True)
def get(real_user, user, id):
    if not id:
        abort(403)
    return id

@enforce(u=users.User)
@authorize(check_admin=True)
def masquerade(real_user, user, u):
    if not u:
        return False
    auth.login(u, redirect_after=False)
    return True

@enforce(u=users.User)
@authorize(check_admin=True)
def pretend(real_user, user, u):
    if not u:
        return False
    auth.pretend(u, url=None)
    return True

@enforce()
@authorize(check_admin=True)
def stop_pretending(real_user, user):
    auth.stop_pretending(url=None)
    return True
    

@enforce(u=users.User, is_active=bool, default_timezone=int)
@authorize()
def edit(real_user, user, u, **kwargs):
    """
    Editing of the campaigns. Supports editing one param at a time. Uses the FieldEditor
    paradigm.
    """
    if not u or not(real_user.is_admin() or real_user.id == u.id):
        raise ClientException('User not found', code=NOT_FOUND, field='u')
    
    editor = Editor()
    editor.edit(real_user, user, u, **kwargs)
    return u

class EditForm(formencode.Schema):
    role = formencode.All(fv.UnicodeString(not_empty=False), fv.OneOf(ROLES))
    password = formencode.All(fv.UnicodeString(not_empty=False), fv.MaxLength(32))
    first_name = formencode.All(fv.UnicodeString(not_empty=False), fv.MaxLength(64))
    last_name = formencode.All(fv.UnicodeString(not_empty=False), fv.MaxLength(64))
    default_timezone = fv.Int(not_empty=False)
    is_active = fv.Bool(not_empty=False)

class Editor(FieldEditor):
    def __init__(self):
        super(Editor, self).__init__(EDIT_FIELDS, ADMIN_EDIT_FIELDS, EditForm)
    
    def edit(self, real_user, user, u, *args, **kwargs):
        self.real_user = real_user
        self.user = user
        self.u = u
        return super(Editor, self).edit(real_user, user, u, *args, **kwargs)

    def edit_role(self, real_user, user, u, key, param):
        self._edit_generic('Role', u, key, param, can_be_none=False)
    
    def edit_password(self, real_user, user, u, key, param):
        self._edit_generic('Password', u, key, param, can_be_none=False)
    
    def edit_username(self, real_user, user, u, key, param):
        self._edit_generic('Username', u, key, param, can_be_none=False)
    
    def edit_first_name(self, real_user, user, u, key, param):
        self._edit_generic('First Name', u, key, param, can_be_none=False)
    
    def edit_last_name(self, real_user, user, u, key, param):
        self._edit_generic('Last Name', u, key, param, can_be_none=False)
    
    def edit_default_timezone(self, real_user, user, u, key, param):
        old = u.default_timezone
        u.set_timezone_int(param)
        self.log('Timezone', key, old, u.default_timezone)
    
    def edit_is_active(self, real_user, user, u, key, param):
        self._edit_generic('IsActive', u, key, param, can_be_none=False)
