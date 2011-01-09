from tethr.lib.base import h, logger
from tethr.model import Session, users
import sqlalchemy as sa
from pylons.controllers.util import abort

from tethr.lib import auth

from pylons_common.lib.utils import objectify
from pylons_common.lib.date import convert_date
from pylons_common.lib.exceptions import *
from pylons_common.web.validation import validate
from pylons_common.lib.decorators import enforce as base_enforce, zipargs, stackable

import formencode.validators as fv

"""
    @enforce MUST be specified before @auth on your api functions. @enforce will convert strings to
    proper DB objects when coming in from the web service. @auth relies on there being proper DB
    objects to do must_own authorization.
"""

def enforce(**types):
    """
    Assumes all arguments are unicode strings, and converts or resolves them to more complex objects.
    If a type of the form [Type] is specified, the arguments will be interpreted as a comma-delimited
    list of strings that will be converted to a list of complex objects. 
    """
    
    # put any defaults here...
    types.setdefault('user', users.User)
    types.setdefault('real_user', users.User)
    
    return base_enforce(Session, **types)
    
def authorize(must_own=None, must_own_if_present=None, check_admin=False, has_role=None):
    
    """
    Authorization checking. Will make sure the user is an admin if you want. And it will verify
    ownership of a db object or multiple db objects.
    
    :param must_own: a string name of a parameter which will have the object to validate. This can be a list.
    """
    @stackable
    def decorator(fn):
        
        @zipargs(fn)
        def new(**kwargs):
            
            # find the user
            user = kwargs.get('real_user') or kwargs.get('user')
            if user is None:
                try:
                    user = auth.get_real_user()
                except TypeError, e:
                    user = None
            
            if not user:
                raise ClientException("Please Login!", INCOMPLETE, field='user')
            
            if must_own:
                # user.must_own takes a list of objects. This allows the user to pass in a single
                # param name, or multiple names.
                mo = must_own
                if not isinstance(mo, list) and not isinstance(mo, tuple):
                    mo = [mo]
                
                #pull the objects that correspond to the param names from the function's args.
                mo_obj_list = []
                for var in mo:
                    if var not in kwargs:
                        raise ClientException("Parameter '%s' not found in function arguments." % (var), NOT_FOUND, field=var)
                    mo_obj_list.append(kwargs[var])
                
                user.must_own(*mo_obj_list)
            
            if must_own_if_present:
                # user.must_own takes a list of objects. This allows the user to pass in a single
                # param name, or multiple names.
                mo = must_own_if_present
                if not isinstance(mo, list) and not isinstance(mo, tuple):
                    mo = [mo]
                
                #pull the objects that correspond to the param names from the function's args.
                mo_obj_list = []
                for var in mo:
                    if var in kwargs and kwargs[var] != None:
                        mo_obj_list.append(kwargs[var])
                
                if mo_obj_list:
                    user.must_own(*mo_obj_list)
            
            elif check_admin:
                if not user.is_admin():
                    raise ClientException("User must be an admin", FORBIDDEN)

            if has_role:
                if user.role != has_role:
                    raise ClientException("User must be in role %s" % has_role, FORBIDDEN)
            
            return fn(**kwargs)
            
        return new
    return decorator

class ConvertDate(fv.FancyValidator):
    def _to_python(self, value, state):
        
        try:
            value = convert_date(value)
        except (ValueError,), e:
            raise fv.Invalid(e.args[0], value, state)
        
        return value

class FieldEditor(object):
    """
    The edit functions for a given object are big and tend to be error prone.
    This class allows you to just specify a validator class, the params you want
    to edit, and some functions to edit those params.
    
    This class will handle editing of one variable at a time, it will catch and
    package up multiple errors, and it will do general authorization.
    
    You just extend it and add your edit functions with name edit_<param_name>
    Then you instantiate and call edit(). Example function:
    
    def edit_budget(actual_user, user, campaign, key, value):
        raise exceptions.ClientException('OMG bad shit is happening!', field=key)
    
    'key' would be 'budget'
    
    Notes:
    
    * If the user is not an admin and he tries ot edit an admin field, the editor
      will just ignore the field as if he had not specified it.
    * Your editing can work one param at a time.
      so /api/v1/campaign/edit?name=my+name
      /api/v1/campaign/edit?key=name&value=my+name are equivalent
    * Your field editing functions can be passed None
      so /api/v1/campaign/edit?cpc= would unset the CPC.
      If you dont want to accept None, check for it in your edit_ function, not
      in the validator.
    * You must do object ownership authorization outside of this editor. The only
      auth this thing does is an admin check for the editing of admin fields.
      Use the @auth(must_own='asd') on your edit api function.
    * Your edit_ functions can raise ClientExceptions. They will be packaged up in
      a CompoundException and be returned to the client side as a collection.
      If you raise an AdrollException, it will get through to the error middleware.
    """
    
    def __init__(self, fields, admin_fields, validator):
        self.validator = validator
        self.fields = fields
        self.admin_fields = admin_fields
    
    def _edit_generic(self, name, obj, key, param, can_be_none=True):
        if not can_be_none and param == None:
            raise exceptions.ClientException('Please enter a %s' % name, field=key)
        
        old = getattr(obj, key)
        setattr(obj, key, param)
        self.log(name, key, old, getattr(obj, key))
    
    def log(self, field, key, old_val, new_val):
        logger.info('%s edited by %s: %s (%s) = %s from %s' % (self.object, self.actual_user, field, key, new_val, old_val))
    
    def edit(self, actual_user, user, obj, key=None, value=None, **kwargs):
        
        self.actual_user = actual_user
        self.user = user
        self.object = obj
        self.params = kwargs
        
        # for the single field edit
        if key and value != None and key not in kwargs:
            kwargs[key] = value
        
        # There is no authorization check in here. This is effectively it.
        # If the user is not an admin, the admin fields are stripped out. 
        editable_keys = set(actual_user.is_admin() and (self.fields + self.admin_fields) or self.fields)
        
        # is there anything we can edit?
        to_edit = [k for k in kwargs.keys() if k in editable_keys]
        if not to_edit:
            raise ClientException('Specify some parameters to edit, please.', code=INCOMPLETE)
        
        # we fill out the kwargs so we dont piss off the validator. hack. poo. Must have all
        # fields as the validator will too.
        for k in self.fields + self.admin_fields:
            if k not in kwargs or k not in editable_keys:
                kwargs[k] = None
        
        params = validate(self.validator, **kwargs)
        
        #this is for collecting errors. 
        error = CompoundException('Editing issues!', code=FAIL)
        
        # only go through the keys that we got in the original call/request (to_edit)
        for k in to_edit:
            if k not in editable_keys: continue
            param = params[k]
            
            fn_name = 'edit_%s' % k
            if hasattr(self, fn_name):
                
                try:
                    results = getattr(self, fn_name)(actual_user, user, obj, k, param)
                except ClientException, e:
                    # if error from editing, we will package it up so as to
                    # return all errors at once
                    error.add(e)
            else:
                #this is an adroll exception cause it should bubble up to a WebApp email
                raise AppException('Cannot find %s edit function! :(' % fn_name, code=INCOMPLETE)
        
        if error.has_exceptions:
            raise error
        
        Session.flush()
        
        return True

import user
import error
