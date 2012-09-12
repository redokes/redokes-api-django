import logging
import redokes.util
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django import template
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission

class Action(object):
    util = redokes.util
    def init_defaults(self):
        self.request = None
        self.parser = None
        self.action = None
        self.template = ''
        self.redirect = ''
        self.params = {}
        self.do_render = True
        self.front_controller = None
        self.auto_template = True
        self.output_type = 'html'
        self.access = None
        self.params = {}
    
    def __init__(self, front_controller, *args, **kwargs):
        self.init_defaults()
        
        #Setup items we get from front controller
        self.front_controller = front_controller
        self.request = front_controller.request_parser.request
        self.parser = front_controller.request_parser
        self.action = front_controller.request_parser.action
        
        #Apply the kwargs
        self.util.apply_config(self, kwargs)
        
        #Set the front controller to be in the template
        self.set_param('_front_controller', self.front_controller)
        
        #Initialize the logger
#        self.logger = logging.getLogger("nooga")
        
        #Run the init method
        self.init()
        
         # check if we need to automatically set the template
        if self.auto_template:
            self.auto_set_template()
        
    def init(self):
        pass
    
    def user_can_access(self, method_name):
        # Check if all methods are public
        if self.access is None:
            return True
        else:
            # Get the logged in user
            user = self.get_user()
            
            # Methods are private so check access
            permissions = ['admin']
            permission_info = {}
            
            # Check if specific method access is defined
            if method_name in self.access:
                permission_info = self.access[method_name]
            elif '*' in self.access:
                permission_info = self.access['*']
            
            #Check if not none and reset
            if permission_info is not None:
                permissions = []
            
            #Add all permissions
            if type(permission_info) is str:
                permissions.append(permission_info)
            elif permission_info is not None:
                # check group
                if 'group' in permission_info:
                    # check if user is in group
                    groups = permission_info['group']
                    if type(groups) is str:
                        groups = [groups]
                    group_set = Group.objects.filter(name__in=groups).prefetch_related()
                    for group in group_set:
                        group_permissions = list(group.permissions.all())
                        permissions = permissions + group_permissions
                
                # check access                    
                if 'access' in permission_info:
                    access_list = permission_info['access']
                    if type(access_list) is str:
                        access_list = [access_list]
                    permissions = permissions + access_list
                    
                    if "admin" in permissions:
                        if not user.is_superuser:
                            return False
            else:
                permissions = None
            
            # Check perms
            if permissions is None:
                return True
            elif not len(permissions):
                return False
            else:
                return user.has_perms(permissions)
    
    def get_template_name(self):
        return '%s/%s/%s.html' % (self.parser.module, self.parser.controller, self.parser.action)
    
    def auto_set_template(self):
        self.set_template(self.get_template_name())
    
    def template_exists(self, template_name):
        try:
            template.loader.get_template(template_name)
            return True
        except template.TemplateDoesNotExist:
            return False
        return False
    
    def run(self):
        return self.action_call()
    
    def catch(self):
        """
        Catches an unknown action.
        By default all this method will do is raise a 404 error.
        Override to provide custom redirection
        """
        raise Http404
    
    def forward(self, action, module=None, controller=None):
        self.parser.action = action
        self.action = action
        if module is not None:
            self.parser.module = module
        if controller is not None:
            self.parser.controller = controller
        return self.front_controller.run()
        
    def action_call(self):
        """
        Calls an action if it exists, or else calls the catch method
        """
        #Check if the action exists
        if self.action_exists() is False:
            return self.catch()
        
        # Check permissions
        if self.user_can_access(self.get_action_method_name()):
            #Run the action method
            return getattr(self, self.get_action_method_name())()
        else:
            self.output_type = '403'
    
    def get_action_method_name(self):
        return self.front_controller.request_parser.get_action_name(self.action)
    
    def action_exists(self):
        #Check if the view instance has the action
        return hasattr(self, self.get_action_method_name())
    
    def render_template(self, template, context):
        return render_to_response(template, context, context_instance=RequestContext(self.request))
    
    def set_template(self, template_name):
        if self.template_exists(template_name):
            self.template = template_name
    
    def set_response_param(self, key, value=None):
        self.front_controller.response_manager.set_param(key, value)
        
    def set_response_params(self, params):
        self.front_controller.response_manager.set_params(params)
        
    def update_response_params(self, params):
        self.front_controller.response_manager.update_params(params)
    
    def set_param(self, key, value=None):
        self.params[key] = value
    
    def set_params(self, dictionary):
        self.params.update(dictionary)
        
    def send_headers(self):
        method_name = 'get_output_%s' % self.output_type
        if hasattr(self, method_name):
            return getattr(self, method_name)()
    
    def get_output_html(self):
        return self.render_template(self.template, self.params)
    
    def get_output_403(self):
        return HttpResponseForbidden("Default 403 template")
    
    def set_redirect(self, url):
        self.redirect = url
        self.output_type = 'redirect'
    
    def get_output_redirect(self):
        return HttpResponseRedirect(self.redirect)
    
    def set_request_param(self, key, value):
        self.front_controller.request_parser.set_param(key, value)
    
    def get_request_param(self, key, value=None):
        return self.front_controller.request_parser.get_param(key, value)
    
    def get_request_params(self):
        return self.front_controller.request_parser.params
    
    def get_response_params(self):
        return self.front_controller.response_manager.get_params()
    
    def get_user(self):
        return self.front_controller.request_parser.request.user
    
    def get_cache_key(self, *args, **kwargs):
        return self.generate_cache_key(self, self.front_controller.request_parser.action, *args, **kwargs)
    
    @staticmethod
    def generate_cache_key(instance, *args, **kwargs):
        parts = instance.__module__.lower().split('.')
        parts += args
        for key in sorted(kwargs.iterkeys()):
            parts.append(str(key))
            parts.append(str(kwargs[key]))
        return '_'.join(parts)
        
