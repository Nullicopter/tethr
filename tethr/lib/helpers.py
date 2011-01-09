
import pylons
from pylons import session, request, tmpl_context as c
from pylons import url as p_url
from paste.deploy.converters import asbool

"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

def url_for(*args, **kwargs):
    """
    """
    
    # pylons 1.0: they got rid of url_for. And it doesnt remember your params anymore.
    # This is a pain in the ass. We have some code that uses url_for outside of a web request
    # context. Turns out pylons.url is only registered in a web request context. So we
    # revert to the old, depricated url_for in those cases. 
    has_url = bool(getattr(pylons.url.____local__, 'objects', None))
    if has_url:
        fn = p_url.current
        if kwargs.get('controller'): #if they specify the controller, use the fn without memory
            fn = p_url
    else:
        from routes import url_for as fn
    
    return fn(*args, **kwargs)

def api_url(module, function, **kwargs):
    """
    Gets the url for an api call.
    
    Convenience function so I dont have to remember all the params. 
    """
    return url_for(controller='api', action='dispatch', version=1, module=module, function=function, **kwargs)

def static_url(type, filename):
    """
    Generates urls to static content.
    It is useful as it automatically appends hash specific to the push in order
    to ensure that the expires header functions correctly.

    :Parameters:
    -`type`: 'c', 'f', 'i' or 'j' 
    -`filename`: the path to the file relative to the respective asset directory.
    """
    return "/%s/%s" % (type, filename)

def js_url(filename):
    """
    """
    return "/j/%s" % (filename)

def has_request_object():
    """
    Sometimes we get
    
    TypeError: No object (name: request) has been registered for this thread
    
    when trying to access the request object. You can use this to check to make
    sure the request object is here.
    """
    return getattr(pylons.request.____local__, 'objects', None)
    
def is_production():
    """
    is this a production server? (may affect things like https://)
    """
    return asbool(pylons.config.get('is_production'))
