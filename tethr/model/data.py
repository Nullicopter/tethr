import sqlalchemy as sa
from sqlalchemy.orm import relation, backref
from tethr.model.meta import Session, Base
from datetime import datetime

from pylons_common.lib import exceptions, date
import re

TYPE_WORK = u'work'
TYPE_HOME = u'home'
TYPE_MOBILE = u'mobile'

def now():
    return datetime.utcnow()

class DataHandler(object):
    
    def __init__(self, data):
        self.data = data
    
    @property
    def normalized(self):
        return self.data.strip()

class PhoneHandler(DataHandler):
    @property
    def normalized(self):
        return re.sub('[^0-9]', '', self.data).strip()

class EmailHandler(DataHandler):
    @property
    def normalized(self):
        return re.sub(r'(\+[^@]*)?', '', self.data.strip().lower())

class DataPoint(Base):
    """
    Stores a single data point
    """
    __tablename__ = "data_points"

    id = sa.Column(sa.Integer, primary_key=True)
    
    # email, name, blah blah
    key = sa.Column(sa.Unicode(64), nullable=False, index=True)
    
    #work, home, etc.
    type = sa.Column(sa.Unicode(16), nullable=False)
    value = sa.Column(sa.Text())
    
    owner = relation("User", backref=backref("data_points", cascade="all"))
    owner_id = sa.Column(sa.Integer, sa.ForeignKey('users.id'), nullable=False)
    
    profile = relation("Profile", backref=backref("data_points", cascade="all"))
    profile_id = sa.Column(sa.Integer, sa.ForeignKey('profiles.id'), nullable=False)
    
    created_date = sa.Column(sa.DateTime, nullable=False, default=now)
    
    is_active = sa.Column(sa.Boolean, nullable=False, default=True)
    
    def __repr__(self):
        return u'DataPoint(%s, owner: %s, profile: %s, k: %r, v: %r)' % (self.id, self.owner_id, self.profile_id, self.key, self.value)

HANDLERS = {
    'email': EmailHandler,
    'phone': PhoneHandler
}

def get_handler(key, value):
    cls = HANDLERS.get(key, DataHandler)
    return cls(value)