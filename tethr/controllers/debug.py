from tethr.lib.base import *

class DebugController(BaseController):
    """
    Junk we need for debugging
    """
    
    # dont use client async. We dont want these queries showing up in the query analyzer...
    def explain(self):
        """
        Used in the development interface to explain queries.
        """
        r = Session.execute("EXPLAIN %s" % request.params['q'])
        result = ""
        for line in r.fetchall():
            result += line.values()[0].replace(' ', '&nbsp;') +"<br/>"
        return result
