from tethr.api import enforce, logger, validate, h, authorize, \
                    AppException, ClientException, CompoundException, \
                    INVALID, NOT_FOUND, FORBIDDEN, abort

"""
This module just creates errors. It is useful for blackbox testing the api
(and our middleware)'s error handling abilities
"""

@enforce(type=unicode, anint=int, abool=bool)
@authorize(check_admin=True)
def explode(real_user, user, type=None, **kw):
    """
    An action to test the error handling of the stack. The tests use this.
    """
    return explode_no_auth(real_user, user, type=type, **kw)

@enforce(type=unicode, anint=int, abool=bool)
def explode_no_auth(real_user, user, type=None, **kw):
    """
    An action to test the error handling of the stack. The tests use this.
    """
    if type == 'app':
        raise AppException('This is an app exception!', code=INVALID, field='type')
    elif type == 'client':
        raise ClientException('Oh Noes, ClientException!', code=INVALID, field='type')
    elif type == 'client404':
        raise ClientException('Oh Noes, ClientException NOT FOUND!', code=NOT_FOUND, field='type')
    elif type == 'client403':
        raise ClientException('Oh Noes, ClientException FORBIDDEN!', code=FORBIDDEN, field='type')
    elif type == 'explosion':
        1/0
    elif type == 'http':
        abort(404, 'This thing was not found!')
    elif type == 'validation':
        class Rawr(formencode.Schema):
            meow = fv.Number()
        scrubbed = validate(Rawr, meow='zzzz')
    
    return kw

@enforce(error=unicode)
def jserror(actual_user, user, error):
    
    logger.info('JS ERROR! actual %s; %s with error: %s' % (actual_user, user, error))
    
    return True
    
    