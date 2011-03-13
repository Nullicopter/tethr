import sqlalchemy as sa
from sqlalchemy.orm import relationship, backref
from tethr.model.meta import Session, Base
from tethr.model import STATUS_ACCEPTED, STATUS_REJECTED, STATUS_PENDING, data

from datetime import datetime

from pylons_common.lib import exceptions, date
from pylons_common.lib.utils import uuid

from collections import defaultdict as dd

def now():
    return datetime.utcnow()
    
class Profile(Base):

    __tablename__ = "profiles"

    id = sa.Column(sa.Integer, primary_key=True)
    
    eid = sa.Column(sa.Unicode(64), nullable=False, unique=True, index=True, default=uuid)
    
    user = relationship("User", backref=backref("profile", uselist=False, cascade="all"))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=True, index=True)
    
    #: is this profile active?
    is_active = sa.Column(sa.Boolean, nullable=False, default=True)
    
    created_date = sa.Column(sa.DateTime, nullable=False, default=now)
    
    def __repr__(self):
        return "%s(%r,user:%r)" % (self.__class__.__name__, self.id, self.user_id)

    @property
    def url(self):
        # import code for encoding urls and generating md5 hashes
        import urllib, hashlib, pylons
        
        data = self.fetch_data()
        email = None
        for d in data:
            if d.key == 'email':
                email = d.value
        
        default = pylons.config.get('pylons_url') + '/i/icons/default_user.png'
        
        if email:
            size = 40
            
            # construct the url
            gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?"
            gravatar_url += urllib.urlencode({'d':default, 's':str(size)})
            
            return gravatar_url
        
        return default


    def deactivate(self):
        """
        """
        self.is_active = False
    
    def teather(self, other_profile):
        """
        same as following. self.teather(other) means the current profile is following 'other'
        """
        q = Session.query(Teather)
        q = q.filter(Teather.teathered_profile_id==other_profile.id)
        existing = q.filter(Teather.owning_profile_id==self.id).first()
        
        if existing: return existing
        
        q = Session.query(Teather).filter(Teather.owning_profile_id==other_profile.id)
        recip = q.filter(Teather.teathered_profile_id==self.id).first()
        
        if recip:
            new = recip.accept()
        else:
            new = Teather(owning_profile=self, teathered_profile=other_profile, status=STATUS_PENDING)
            Session.add(new)
        
        return new
    
    def add_data(self, user, key, value, type=u''):
        """
        Blindly adds data to a profile
        """
        if not user:
            raise exceptions.AppException('Gimmie a user', field=u'user', code=exceptions.INVALID)
        
        #we overwrite any keys that were created by this user. 
        q = Session.query(data.DataPoint).filter(data.DataPoint.profile==self)
        q = q.filter(data.DataPoint.key==key)
        q = q.filter(data.DataPoint.owner==user)
        
        d = q.first()
        handler = data.get_handler(key, value)
        
        if d:
            d.value = handler.normalized
        else:
            d = data.DataPoint(profile=self, owner=user, key=key, value=handler.normalized, type=type)
            Session.add(d)
        return d
    
    def fetch_teathers(self, status=None, order_by='teathers.created_date', order_sort=sa.asc, teathered_profile=None):
        q = Session.query(Teather).filter(Teather.owning_profile_id==self.id)
        if status:
            q = q.filter(status=status)
        if teathered_profile:
            q = q.filter(Teather.teathered_profile==teathered_profile)
        q.order_by(order_sort(order_by))
        
        return q.all()
    
    def fetch_teathered_profiles(self, status=None):
        tethers = self.fetch_teathers(status=status)
        
        return [t.teathered_profile for t in tethers]
    
    def fetch_data(self, user=None):
        """
        :param user: user who will see the data. When user == None, will get ALL data points
        """
        q = Session.query(data.DataPoint).filter(data.DataPoint.profile_id==self.id)
        if user:
            owners = [user.id]
            if self.user:
                owners.append(self.user.id)
            
            q = q.filter(data.DataPoint.owner_id.in_(owners))
            
            data_points = q.all()
            
            # if this profile wanted to be connected to the viewing user, the viewing user can
            # see all the user's info.
            teather = self.fetch_teathers(teathered_profile=user.profile)
            if not teather:
                #we have a special case where we should return the user's name always
                points = []
                for dp in data_points:
                    if dp.owner == user or dp.key == 'name':
                        points.append(dp)
                data_points = points
            # else, can see all user's info
            
        else:
            data_points = q.all()
        
        points = dd(lambda: [])
        for dp in data_points:
            sig = '%s:%s' % (dp.key, dp.type)
            
            #the data from user who owns the profile is more important
            if dp.owner == self.user:
                points[sig] = [dp]+points[sig]
            else:
                points[sig].append(dp)
        
        return [v[0] for k, v in points.items() if v]
    
    @classmethod
    def find_unclaimed(cls, email):
        
        P = cls
        DP = data.DataPoint
        
        handler = data.get_handler('email', email)
        profile = Session.query(P).join(DP).filter(P.user==None).filter(DP.key==u'email').filter(DP.value==handler.normalized).first()
        return profile

class Teather(Base):
    """
    Stores a connection to another profile
    """
    __tablename__ = "teathers"

    id = sa.Column(sa.Integer, primary_key=True)
    
    eid = sa.Column(sa.Unicode(64), nullable=False, unique=True, index=True, default=uuid)
    
    status = sa.Column(sa.Unicode(16), nullable=False)
    
    owning_profile_id = sa.Column(sa.Integer, sa.ForeignKey('profiles.id'), nullable=False, index=True)
    owning_profile = relationship("Profile", primaryjoin=owning_profile_id==Profile.id, backref=backref("owned_teathers", cascade="all"))
    
    teathered_profile_id = sa.Column(sa.Integer, sa.ForeignKey('profiles.id'), nullable=False, index=True)
    teathered_profile = relationship("Profile", primaryjoin=teathered_profile_id==Profile.id, backref=backref("inbound_teathers", cascade="all"))
    
    reciprocated_teather_id = sa.Column(sa.Integer, sa.ForeignKey('teathers.id'), nullable=True, index=True, default=None)
    reciprocated_teather = relationship("Teather", remote_side=id, backref=backref("original_teather", uselist=False))
    
    created_date = sa.Column(sa.DateTime, nullable=False, default=now)
    
    def __repr__(self):
        return u'Teather(%s, owned by: %s, teathered to: %s, status: %s, recip: %s)' % (self.id,
                    self.owning_profile_id, self.teathered_profile_id, self.status,
                    self.reciprocated_teather_id)
    
    def reject(self):
        self.status = STATUS_REJECTED
    
    def accept(self):
        if self.status != STATUS_ACCEPTED and not self.reciprocated_teather_id:
            
            new = Teather(owning_profile=self.teathered_profile, teathered_profile=self.owning_profile,
                         status=STATUS_ACCEPTED, reciprocated_teather=None)
            Session.add(new)
            
            self.status = STATUS_ACCEPTED
            self.reciprocated_teather = new
            
            return new
        return None