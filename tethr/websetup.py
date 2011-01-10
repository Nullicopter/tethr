"""Setup the tethr application"""
import logging

import pylons.test

from tethr.config.environment import load_environment
from tethr.model.meta import Session, Base
from tethr.model.users import User, UserPreference
from tethr.model.profiles import Teather, Profile
from tethr.model.data import DataPoint

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
    """Place any commands to setup tethr here"""
    # Don't reload the app if it was loaded under the testing environment
    #if not pylons.test.pylonsapp:
    config = load_environment(conf.global_conf, conf.local_conf)
    
    engine = config['pylons.app_globals'].sa_default_engine
    
    #init_model(engine)
    
    # Create the tables if they don't already exist
    Base.metadata.create_all(bind=engine)
