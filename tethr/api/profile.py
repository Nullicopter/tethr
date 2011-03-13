from tethr.api import enforce, logger, validate, h, authorize, \
                    AppException, ClientException, CompoundException, \
                    INVALID, NOT_FOUND, FORBIDDEN, abort, FieldEditor, auth

from tethr.model import users, Session, profiles, data
from tethr.model.data import TYPE_WORK, TYPE_HOME, TYPE_MOBILE
import sqlalchemy as sa

import formencode
import formencode.validators as fv

ID_PARAM = 'u'

EDIT_FIELDS = []
ADMIN_EDIT_FIELDS = ['is_active']

class TeatherForm(formencode.Schema):
    email = fv.Email(not_empty=True)

@enforce(email=unicode, profile=profiles.Profile)
@authorize()
def teather(real_user, user, profile=None, email=None, **kw):
    """
    Will teather/follow another user
    
    kw can be extra data to be asscoiated with the teather. Passing a type is done
    by using a colon. i.e.
    
    kw['phone'] = '415-343-1234' # would just add a phone number
    kw['phone:work'] = '415-343-1234' # would add a phone number with type work
    
    also, notes are associated the same way as everything else.
    
    kw['notes'] = 'We met at the xyz blah'
    """
    if (not profile and not email) or not user.profile:
        abort(403)
    
    profile = get(real_user, user, profile=profile, email=email)
    if not profile and not email:
        abort(403)
    
    #create unclaimed
    elif not profile:
        email = validate(TeatherForm, email=email).email
        
        profile = profiles.Profile(user=None)
        Session.add(profile)
        Session.flush()
    
    add_data(real_user, user, profile, **kw)
    
    #attach an email address...
    if not email and profile.user:
        email = profile.user.email
    
    
    #all_data = profile.fetch_data()
    #has_email = False
    #for d in all_data:
    #    if d.key == 'email':
    #        has_email = True
    #        if (email and data.EmailHandler.normalize(email) != d.value):
    #            profile.add_data(user, 'email', email, type=d.type)
    
    #if not has_email and not email:
    #    raise ClientException('Need to specify an email address!')
    #elif not has_email:
    
    if email:
        profile.add_data(user, 'email', email)
    
    t = user.profile.teather(profile)
    Session.flush()
    
    return t

@enforce(profile=profiles.Profile)
@authorize()
def add_data(real_user, user, profile, **kw):
    """
    can pass in data like 'phone:work'='555-555-5555'
    """
    if not profile:
        abort(403)
    
    class KVForm(formencode.Schema):
        key = fv.UnicodeString(not_empty=True, min=2, max=64)
        type = fv.OneOf([TYPE_WORK, TYPE_HOME, TYPE_MOBILE], not_empty=False)
        value = fv.UnicodeString(not_empty=True, min=2, max=1024)
    
    for k, v in kw.items():
        type = None
        s = k.split(':', 1)
        if len(s) == 2:
            k, type = s
        
        if v:
            scrubbed = validate(KVForm, key=k, value=v, type=type)
            
            profile.add_data(user, scrubbed.key, scrubbed.value, type=scrubbed.type)
    
    Session.flush()
    
    return profile

@enforce(profile=profiles.Profile, email=unicode)
@authorize()
def get(real_user, user, profile=None, email=None):
    
    if profile: return profile
    
    P = profiles.Profile
    DP = data.DataPoint
    
    #fetch all
    if not profile and not email:
        return user.profile.fetch_teathers()
    
    # for email
    handler = data.get_handler('email', email)
    profile = Session.query(P).join(DP).filter(DP.key==u'email').filter(DP.value==handler.normalized).first()
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

##
### No expose to webservice
##

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