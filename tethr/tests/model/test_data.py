from datetime import date, timedelta

from tethr.model import users, profiles, STATUS_ACCEPTED, STATUS_REJECTED, fixture_helpers as fh, data
from tethr.tests import *

class TestProfiles(TestController):
    def test_email_handler(self):
        
        def test_norm(inp, out):
            ha = data.EmailHandler(inp)
            assert ha.normalized == out
        
        test_norm('Blah.blah@omgwow.cOm', 'blah.blah@omgwow.com')
        test_norm('Blah.blah+@omgwow.cOm', 'blah.blah@omgwow.com')
        test_norm('Blah.blah+this_and_that@omgwow.cOm', 'blah.blah@omgwow.com')
    
    def test_phone_handler(self):
        
        def test_norm(inp, out):
            ha = data.PhoneHandler(inp)
            assert ha.normalized == out
        
        test_norm('510 234 3452', '5102343452')
        test_norm('+1 510-234-3452', '15102343452')
        test_norm('+1 510.234_3452  ', '15102343452')