from tethr.lib.base import *

class IndexController(BaseController):
    """
    """
    def index(self):
        return self.render('/index/index.html')

