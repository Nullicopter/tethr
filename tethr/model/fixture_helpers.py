"""
To help you writing tests. Should be able to create each type of object in the system
with no other inputs. 
"""
from tethr.model import Session, users, profiles, data
from pylons_common.lib import utils

def create_unique_str(pre=u'', extra=u"\u00bf"):
    """
    @param pre: The string to prefix the unique string with. Defaults to
                nothing.
    @param extra: The string to append to the unique string. Default to a
                  unicode character.
    @return: A unique string.
    """
    return u"%s%s%s" % (pre, utils.uuid(), extra)

def create_email_address():

    return create_unique_str(u'email') + u"@email.com"

def create_str(length=None):
        
        letters = ' abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        key = []
        
        l = length or random.randint(30, 50)
        
        for i in range(l):
            key.append(letters[random.randint(0, len(letters)-1)])
        
        return ''.join(key)

def create_user(is_admin=False, **kw):

    kw.setdefault("email", create_email_address())
    kw.setdefault("username", create_unique_str(u'user', extra=u''))
    kw.setdefault("password", u'testpassword')
    
    if is_admin:
        kw.setdefault("role", users.ROLE_ADMIN)
    else:
        kw.setdefault("role", users.ROLE_USER)

    user = users.User(**kw)
    Session.add(user)
    Session.flush()
    return user

def create_profile(user='create', **kw):
    if user == 'create':
        user = create_user()
    
    kw.setdefault("is_active", True)
    kw.setdefault("user", user)
    kw.setdefault('name', create_unique_str(pre=u'name'))
    kw.setdefault('email', user and user.email or create_email_address())
    
    name = kw.pop('name')
    email = kw.pop('email')
    
    profile = profiles.Profile(**kw)
    Session.add(profile)
    
    if user:
        profile.add_data(user, 'name', name)
        profile.add_data(user, 'email', email)
    
    Session.flush()
    return profile