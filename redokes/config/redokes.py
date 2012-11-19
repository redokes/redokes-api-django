from django.conf import settings



class RedokesConfig(object):
    
    config = None
    
    def init_defaults(self):
        RedokesConfig.config = {
            'default_module': 'index',
            'default_controller': 'index',
            'default_action': 'index',
        }
    
    def __init__(self):
        self.init_defaults();
        RedokesConfig.config.update(getattr(settings, 'REDOKES_CONFIG', {}))
        print 'run init'
    
    @staticmethod
    def getConfig():
        print 'get instance'
        if RedokesConfig.config is None:
            RedokesConfig()
            print RedokesConfig.config
        return RedokesConfig.config