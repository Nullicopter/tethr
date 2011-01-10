"""The application's model objects"""
import datetime
from tethr.model.meta import Session, Base

STATUS_ACCEPTED = u'accepted'
STATUS_REJECTED = u'rejected'
STATUS_PENDING = u'pending'

def init_model(engine):
    """Call me before using any of the tables or classes in the model"""
    Session.configure(bind=engine)
    
    from psycopg2 import extensions
    extensions.register_type(extensions.UNICODE)