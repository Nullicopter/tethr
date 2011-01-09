"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

from paste import fixture
from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test

from pylons_common.lib.log import create_logger
logger = create_logger('tethr.tests')

from pylons_common.lib.utils import objectify
from pylons_common.lib.exceptions import ClientException, CompoundException
import simplejson as json

import formencode

from tethr.model.meta import Session
from tethr.lib.helpers import url_for, api_url

# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

environ = {}

def unjsonify(response, do_objectify=True):
    """
    Takes the response from a client_async-decorated action
    and returns a python object derived from it.
    """
    return objectify(json.loads(response.body))
    
class TestRollback(TestCase):
    
    keep_data = False
    
    def setUp(self):
        self._session = Session
        self.clear()
    
    def tearDown(self):
        if self.keep_data:
            self._session.commit()
        else:
            self._session.rollback()
        self._session.close()
        
    def flush(self):
        self._session.flush()

    def add(self, *args, **kwargs):
        self._session.add(*args, **kwargs)

    def refresh(self, *args, **kwargs):
        self._session.refresh(*args, **kwargs)

    def clear(self):
        self._session.expunge_all()


class TestController(TestRollback):
    
    def __init__(self, *args, **kwargs):
        import sys
        self.wsgiapp = pylons.test.pylonsapp
        self.config = self.wsgiapp.config
        self.app = fixture.TestApp(self.wsgiapp)
        url._push_object(URLGenerator(self.config['routes.map'], environ))
        
        TestRollback.__init__(self, *args, **kwargs)
    
    def get_auth_kw(self):
        
        kw = dict(extra_environ = { 'REMOTE_ADDR' : '127.0.0.1' })
        
        return kw
    
    def login(self, user, password=None, **kw):
        kw.update(self.get_auth_kw())
        
        resp = self.post(url_for(controller='auth', action='login'),
                         dict(username=user.username, password=password or u'testpassword'), **kw)
    
    def pretend(self, user, **kw):
        resp = self.get(url_for(controller='auth', action='pretend', username=user.username))
    
    def __merge_dictionaries__(self, dict, kw):
        """
        Merges the second level of two two level dictionaries together
        """
        
        for k,v in dict.iteritems():
            if kw.has_key(k):
                if (hasattr(v, 'keys')):
                    for kk in v.keys():
                        kw[k][kk] = v[kk]
            else:
                kw[k] = v
    
    def get(self, url, params=None, headers={'Accept': 'text/html'}, **kw):

        dict = self.get_auth_kw()
        self.__merge_dictionaries__(dict, kw)
        response = self.app.get(url, params, headers=headers, **kw)

        return response

    def _convert_unicode(self, obj):
        
        if isinstance(obj, basestring):
            return obj.encode('utf-8')
        return obj
    
    def post(self, url, params=None, headers={'Accept': 'text/html'}, **kw):
        
        auth_dict = self.get_auth_kw()
        self.__merge_dictionaries__(auth_dict, kw)
        # TODO - this is temporary until paste actually allows for unicode input
        # UPDATE - paste won't fix this - paste.fixture.TestApp is getting deprecated
        #          in favor of a different package, WebTest - http://pythonpaste.org/webtest/
        if isinstance(params, dict):
            new_params = {}
            for key in params:
                if isinstance(key, unicode):
                    new_key = key.encode('utf-8')
                else:
                    new_key = key
                if isinstance(params[key], unicode):
                    new_value = params[key].encode('utf-8')
                else:
                    new_value = params[key]
                new_params[new_key] = new_value
            params = new_params
        elif isinstance(params, (list, tuple)):
            for i, pair in enumerate(params):
                if isinstance(pair, (list, tuple)):
                    # assume list of key value pairs
                    if isinstance(pair[0], unicode):
                        key = pair[0].encode('utf-8')
                    else:
                        key = pair[0]
                    if isinstance(pair[1], unicode):
                        value = pair[1].encode('utf-8')
                    else:
                        value = pair[1]
                    params[i] = (key, value)
        return self.app.post(url, params, headers=headers, **kw)
    
    def client_async(self, url, params={}, method='post', assert_success=True, **args):
        args.setdefault('headers', {'Accept': 'application/json'})
        if method == 'post':
            r = self.post(url, params=params, **args)
        else:
            r = self.get(url, **args)
        
        if assert_success:
            assert r.status == 200
        
        r = unjsonify(r)
        return r
    
    def is_sign_in_page(self, response):
        
        if response.status == 302: # redirect
            response = response.follow()
        return "Please Sign In" in response
    
    def throws_exception(self, fn, types=(ClientException, CompoundException, formencode.validators.Invalid)):
        """
        Will return the exception if the function calls one, and false if not.
        
        :param types: a tuple of exception types the except should catch.
        """
        try:
            fn()
            assert 0, 'Should have thrown an exception of %s' % (types,)
        except types, e:
            return e
