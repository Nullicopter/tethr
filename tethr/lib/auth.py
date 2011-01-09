import pylons
from pylons import session, request, tmpl_context as c
import helpers as h

from pylons_common.lib import exceptions

from tethr.model.meta import Session
from tethr.model import users

from pylons_common.lib.log import logger

from datetime import datetime

import sqlalchemy as sa

def authenticate(username, password, redirect_after=True, from_http_auth=False):
    q = Session.query(users.User)
    q = q.filter(sa.or_(users.User.username==username, users.User.email==username))
    u = q.first()
    
    if u and u.is_active and u.does_password_match(password):
        return login(u, redirect_after=redirect_after, from_http_auth=from_http_auth)
    else:
        raise exceptions.ClientException('Email and password do not match.', code=exceptions.MISMATCH, field='password')
    return None

def authenticate_basic_auth():
    header = request.headers.get('Authenticate') or request.headers.get('Authorization')
    logger.info(header)
    if header:
        import base64
        (style, b64) = header.split(' ')
        if style == 'Basic':
            username, password = base64.decodestring(b64).split(':')
            username = unicode(username)
            
            u = authenticate(username, password, redirect_after=False, from_http_auth=True)
            if u: return u
    return False

##
###
##

def login(user, redirect_after=True, from_http_auth=False):
    """
    NOTE - this will also trigger a db flush to save last login date
        calling methods should flush their data beforehand
    @param redirect_after - should we redirect after they sign in to
        whatever url they were looking for? you want to set this to False,
        it you are using a sign-in form that's part of a flow. why do we need to
        explicitly set to False? because a guest user may have tried to access 
        a page ("x") of the site where you need to be logged in (and the path_before_login
        session var was then site). however, the user did not sign in, but then
        later attempts to sign in a new campaign flow. at this point, you don't
        want to redirect to "x".
    """
    # no longer using authkit
    #   sets paste auth ticket with username
    #   uses str() to convert to ascii
    #request.environ['paste.auth_tkt.set_user'](str(user.username))

    # cache user data so we can skip db lookups later
    session['user'] = user.id
    session['real_user'] = user.id
    session['username'] = user.username
    session['real_username'] = user.username
    session['role'] = user.role
    
    #set this for the middleware and the base controller
    session['show_debug'] = can_see_debug_info(user)
    
    if from_http_auth:
        return
    session.save()

    user.last_login_date = datetime.utcnow()

    # Send user back to the page s/he originally wanted to get to
    if redirect_after and session.get('path_before_login'):
        # we only want to do this once, so delete the key from the session after making a copy of it
        where_to_go = session['path_before_login']
        del session['path_before_login']
        session.save()
        return where_to_go
    return None

def can_see_debug_info(user):
    """
    Change this if you have different criteria this if you wanna.
    """
    #is_admin uses the session so dont pass the user
    return is_admin();

def logout():
    
    session.clear()
    session.save()

def pretend(user, url='/'):
    if is_logged_in() and is_admin():
        session['user'] = user.id
        session['username'] = user.username
        session.save()
        if url:
            h.redirect(url)

def stop_pretending(url='/'):
    if is_logged_in():
        session['user'] = session['real_user']
        session['username'] = session['real_username']
        session.save()
        if url:
            h.redirect(url)
    
def redirect_to_sign_in(url=None):
    """
    redirects the user to the sign in page
    while gathering info about where they were going
    so they can be redirected back after sign in

    url param overrides the automatic check so that
    the path to go to after sign in can be specified
    """

    if url:
        session['path_before_login'] = url
    else:
        # NOTE - whith pylons 9.7 the following can be simplified to just request.path_qs
        session['path_before_login'] = request.path_info
        if request.params:
            param_str = '?'
            for i, key in enumerate(request.params):
                if i != 0:
                    param_str += '&'
                param_str += key.encode('utf-8') + '=' + request.params[key].encode('utf-8')
            session['path_before_login'] += param_str
    
    session.save()
    
    return redirect(url_for(controller='auth', action='login'))

def get_user(key='user'):
    """
    Gets the user model object if user has logged on. Will be the pretend
    user if an admin is pretending to be someone.
    Returns/sets a cached copy (from the context c var)
    """
    if getattr(c, key):
        return getattr(c, key)

    user_id = session.get(key)
    if user_id:
        setattr(c, key, Session.query(users.User).outerjoin(users.UserPreference).filter(users.User.id == user_id).first())
        if session['user'] == session['real_user']:
            c.user = c.real_user = getattr(c, key)
    else:
        setattr(c, key, None)
    
    return getattr(c, key)

def get_real_user():
    return get_user('real_user')

def get_user_ip():
    """
    This is not as easy as it should be. HTTP_X_FORWARDED_FOR has a comma separated
    list of IPs with the user's IP and an IP of something that I can only assume
    is in front of our servers.
    """
    
    ip = request.environ.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')
        if len(ip) > 0:
            return ip[0].strip()
    
    return None

def is_logged_in():
    if 'real_user' in session:
        return True
    return False

def is_engineer():
    return is_in_roles([users.ROLE_ENGINEER])
    
def is_admin():
    return is_in_roles([users.ROLE_ADMIN, users.ROLE_ENGINEER])

def is_in_roles(roles):
    
    if not is_logged_in():
        return False
    else:
        role = session.get('role', '')
    return role in roles