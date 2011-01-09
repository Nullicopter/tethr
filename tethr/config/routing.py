"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False
    map.sub_domains = True
    map.sub_domains_ignore = "www"

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    map.connect('/', controller='index', action='index')
    
    # Web API
    # Wraps a safe subset of adroll.api for public consumption.
    map.connect('/api/v{version}/{module}/{function}/{id}', version=1, controller='api', action='dispatch')
    map.connect('/api/v{version}/{module}/{function}', version=1, controller='api', action='dispatch')
    map.connect('/api/v{version}/{module}', version=1, controller='api', action='dispatch')
    
    # Shortened webservice routes.  Meant to be accessed from api.adroll.com per documentation.
    map.connect('/v1/{module}/{function}/{id}', version=1, controller='api', action='dispatch', sub_domain='api')
    map.connect('/v1/{module}/{function}', version=1, controller='api', action='dispatch', sub_domain='api')
    map.connect('/v1/{module}', version=1, controller='api', action='dispatch', sub_domain='api')

    map.connect('/admin', controller='admin/search', action='index')
    
    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')

    return map
