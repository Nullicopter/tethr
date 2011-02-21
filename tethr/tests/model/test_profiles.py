from datetime import date, timedelta

from tethr.model import users, profiles, STATUS_ACCEPTED, STATUS_REJECTED, STATUS_PENDING, fixture_helpers as fh
from tethr.tests import *

class TestProfiles(TestController):
    
    def test_creation(self):
        u = fh.create_user()
        p = fh.create_profile(u)
        self.flush()
        
        l = len(p.data_points)
        assert l == 2
        
        assert p.is_active
        keys = ['name', 'email']
        for dp in p.data_points:
            assert dp.key in keys
    
    def test_teathering_accept(self):
        u = fh.create_user()
        p = fh.create_profile(u)
        
        u2 = fh.create_user()
        p2 = fh.create_profile(u2)
        self.flush()
        
        l = len(p.fetch_teathers())
        assert l == 0
        
        # user u wants to connect to u2
        p.teather(p2)
        self.flush()
        
        teathers = p.fetch_teathers()
        l = len(teathers)
        assert l == 1
        assert teathers[0].owning_profile.id == p.id
        assert teathers[0].teathered_profile.id == p2.id
        assert teathers[0].status == STATUS_PENDING
        assert teathers[0].reciprocated_teather == None
        
        teathers[0].accept()
        self.flush()
        
        teathers = p.fetch_teathers()
        teathers2 = p2.fetch_teathers()
        l = len(teathers)
        l2 = len(teathers2)
        assert l == l2 == 1
        
        assert teathers[0].owning_profile.id == p.id
        assert teathers[0].teathered_profile.id == p2.id
        assert teathers[0].status == STATUS_ACCEPTED
        assert teathers[0].reciprocated_teather.id == teathers2[0].id
        
        assert teathers2[0].owning_profile.id == p2.id
        assert teathers2[0].teathered_profile.id == p.id
        assert teathers2[0].status == STATUS_ACCEPTED
        assert teathers2[0].original_teather.id == teathers[0].id
    
    def test_teathering_reject(self):
        p = fh.create_profile()
        p2 = fh.create_profile()
        self.flush()
        
        # user u wants to connect to u2
        p.teather(p2)
        self.flush()
        
        teathers = p.fetch_teathers()
        l = len(teathers)
        assert l == 1
        assert teathers[0].owning_profile.id == p.id
        assert teathers[0].teathered_profile.id == p2.id
        assert teathers[0].status == STATUS_PENDING
        assert teathers[0].reciprocated_teather == None
        
        # no effin way!
        teathers[0].reject()
        self.flush()
        
        teathers = p.fetch_teathers()
        teathers2 = p2.fetch_teathers()
        l = len(teathers)
        l2 = len(teathers2)
        assert l == 1
        assert l2 == 0
        
        assert teathers[0].owning_profile.id == p.id
        assert teathers[0].teathered_profile.id == p2.id
        assert teathers[0].status == STATUS_REJECTED
        assert teathers[0].reciprocated_teather == None
    
    def test_add_data(self):
        p = fh.create_profile()
        p2 = fh.create_profile(name=u'Joey Walrustitty')
        self.flush()
        
        #p <-> p2; p added p3, p3 did not add p; p3 and p2 NOT connected
        p.teather(p2).accept()
        self.flush()
        
        #this should overwrite
        p2.add_data(p2.user, 'myprop', u'Joey Set This')
        self.flush()
        p2.add_data(p.user, 'myprop', u'p set this')
        self.flush()
        
        p2.add_data(p.user, 'property', u'blah')
        self.flush()
        p2.add_data(p.user, 'property', u'something else')
        self.flush()
        p2.add_data(p.user, 'property', u'something last')
        self.flush()
        
        def test_exp(dps, exp):
            assert len(exp.keys()) == len(dps)
            for dp in dps:
                assert exp[dp.key] == dp.value
        
        exp = {
            'name': u'Joey Walrustitty',
            'myprop': u'Joey Set This',
            'property': u'something last',
            'email': p2.user.email.lower()
        }
        d = p2.fetch_data(user=p.user)
        test_exp(d, exp)
        
    
    def test_teathering_fetch_data(self):
        p = fh.create_profile()
        p2 = fh.create_profile(name=u'Joey Walrustitty')
        p3 = fh.create_profile(name=u'Whateva')
        p4 = fh.create_profile(user=None, name=u'Max Powers')
        self.flush()
        
        #p <-> p2; p added p3, p3 did not add p; p3 and p2 NOT connected
        p.teather(p2).accept()
        p.teather(p3).reject()
        p.teather(p4) #pending to a orphan profile
        self.flush()
        
        p2.add_data(p2.user, 'linkedin', u'blah')
        p2.add_data(p.user, 'name', u'Some Guy')
        p2.add_data(p.user, 'email', p2.user.email) #duplicate, no dupes should come back
        p2.add_data(p.user, 'notes', u'We met at a party!')
        
        p3.add_data(p3.user, 'linkedin', u'omgwow')
        p3.add_data(p.user, 'name', u'Another Guy')
        p3.add_data(p.user, 'email', p3.user.email)
        p3.add_data(p.user, 'notes', u'We met at a BAR!')
        
        p4.add_data(p.user, 'name', u'Max Powers')
        p4.add_data(p.user, 'notes', u'We met at a blah!')
        self.flush()
        
        def test_exp(dps, exp):
            assert len(exp.keys()) == len(dps)
            for dp in dps:
                assert exp[dp.key] == dp.value
        
        exp = {
            'name': u'Joey Walrustitty',
            'email': p2.user.email.lower(),
            'linkedin': u'blah',
            'notes': u'We met at a party!'
        }
        d = p2.fetch_data(user=p.user)
        test_exp(d, exp)
        
        exp = {
            'name': u'Whateva',
            'email': p3.user.email.lower(),
            'notes': u'We met at a BAR!'
        }
        d = p3.fetch_data(user=p.user)
        test_exp(d, exp)
        
        exp = {
            'name': u'Whateva'
        }
        d = p3.fetch_data(user=p2.user) # no connection
        test_exp(d, exp)
        
        exp = {
            'name': u'Max Powers',
            'notes': u'We met at a blah!'
        }
        d = p4.fetch_data(user=p.user)
        test_exp(d, exp)