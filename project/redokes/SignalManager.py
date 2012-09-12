import importlib
from django.dispatch import receiver
from django.conf import settings
from django.db.models import signals

class SignalManager(object):
    signal_names = False
    last_app_name = ''
    
    def __init__(self):
        self.last_app_name = settings.INSTALLED_APPS[-1]
        
        if self.signal_names:
            for signal_name in self.signal_names:
                self.init_signal(signal_name)
    
    def init_signal(self, signal_name):
        signal = getattr(signals, signal_name)
        method_name = 'on_%s' % signal_name
        
        def fire_signal(sender, **kwargs):
            # check if method for event
            if hasattr(self, method_name):
                getattr(self, method_name)(sender, **kwargs)
            
            # check if method for specific app event
            if 'app' in kwargs:
                app_name = kwargs['app'].__name__
                app_name = app_name.replace('.', '_')
                app_name = app_name.replace('_models', '')
                app_method_name = 'on_%s_%s' % (app_name, signal_name)
                if hasattr(self, app_method_name):
                    getattr(self, app_method_name)(sender, **kwargs)
                
                # check if this app is the last app in the installed list
                # warning: this is not reliable if the last app does not have models
                if app_name == self.last_app_name:
                    last_method_name = 'on_last_app_%s' % signal_name
                    if hasattr(self, last_method_name):
                        getattr(self, last_method_name)(sender, **kwargs)
        
        placeholder_method_name = 'sm_%s' % signal_name
        setattr(self, placeholder_method_name, fire_signal)
        getattr(signals, signal_name).connect(fire_signal)