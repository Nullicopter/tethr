"""
"""

from pylons_common.lib.utils import itemize
from tethr.model.profiles import Teather

DATE_FORMAT = '%Y-%m-%d %H:%M:%SZ'
def fdatetime(dt):
    if dt:
        return dt.strftime(DATE_FORMAT)
    return None

def get_data_point(dp):
    return itemize(dp, 'key', 'value', 'type')

class FunctionSerializer(object):
    def __init__(self, real_user=None, user=None):
        self.user = user
        self.real_user = real_user
    
class error:
    class explode: pass
    class explode_no_auth: pass
    class jserror: pass

class user:
    class pretend: pass
    class masquerade: pass
    class stop_pretending: pass
    
    class edit(FunctionSerializer):
        def output(self, u):
            return user.get().output(u)

    class get(FunctionSerializer):
        def output(self, u):
            return itemize(u, 'email', 'display_username', 'is_active', 'first_name', 'last_name', 'default_timezone')
    class set_pref: pass

class profile:
    
    class get(FunctionSerializer):
        def output(self, t):
            
            if isinstance(t, list):
                return [self.output(pro) for pro in t]
            
            if not t:
                return None
            
            if isinstance(t, Teather):
                p = t.teathered_profile
            else:
                p = t
            
            res = itemize(p, 'eid', 'is_active', 'url')
            
            if isinstance(t, Teather):
                res['created_date'] = fdatetime(t.created_date)
            
            res['id'] = res['eid']
            res['user'] = None
            if p.user:
                res['user'] = user.get().output(p.user)
            
            res['data'] = {}
            
            points = p.fetch_data(user=self.user)
            for p in points:
                res['data'][p.type and p.key+':'+p.type or p.key] = p.value
            
            return res
    
    class add_data(FunctionSerializer):
        def output(self, p):
            return profile.get(self.real_user, self.user).output(p)
    
    class teather(FunctionSerializer):
        def output(self, p):
            return profile.get(self.real_user, self.user).output(p)