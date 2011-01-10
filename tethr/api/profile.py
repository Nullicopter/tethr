from tethr.api import enforce, logger, validate, h, authorize, \
                    AppException, ClientException, CompoundException, \
                    INVALID, NOT_FOUND, FORBIDDEN, abort, FieldEditor, auth

from tethr.model import users, Session, profiles, data
import sqlalchemy as sa

import formencode
import formencode.validators as fv

ID_PARAM = 'u'

EDIT_FIELDS = []
ADMIN_EDIT_FIELDS = ['is_active']

class CreateForm(formencode.Schema):
    is_active = fv.Bool(not_empty=False)
    
@enforce(is_active=bool)
def create(user, **params):
    """
    Creates a profile.
    
    DO NOT EXPOSE THIS to the web api. Please.
    """
    if user and user.profile:
        raise AppException('User cannot have an existing profile.', field='user', code=INVALID)
    
    params.setdefault('is_active', True)
    
    scrubbed = validate(CreateForm, **params)
    
    profile = profiles.Profile(user=user, **scrubbed)
    Session.add(profile)
    
    return profile

@enforce(profile=profiles.Profile)
@authorize()
def get(real_user, user, profile):
    if not profile:
        abort(403)
    return profile

@enforce(profile=profiles.Profile, is_active=bool)
@authorize(must_own='profile')
def edit(real_user, user, profile, **kwargs):
    """
    Editing of the campaigns. Supports editing one param at a time. Uses the FieldEditor
    paradigm.
    """
    editor = Editor()
    editor.edit(real_user, user, profile, **kwargs)
    return u

class EditForm(formencode.Schema):
    is_active = fv.Bool(not_empty=False)

class Editor(FieldEditor):
    def __init__(self):
        super(Editor, self).__init__(EDIT_FIELDS, ADMIN_EDIT_FIELDS, EditForm)
    
    def edit_is_active(self, real_user, user, u, key, param):
        self._edit_generic('IsActive', u, key, param, can_be_none=False)
