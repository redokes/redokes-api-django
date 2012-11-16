import logging
from django.http import HttpResponse, HttpRequest
from django.http import Http404
import json

class Parser():
    
    #Constructor
    def __init__(self, request, request_string):
        #Properties
        self.logger = None
        self.request = None
        self.module = 'index'
        self.controller = 'index'
        self.action = 'index'
        self.controller_instance = None
        self.params = {}
        self.args = []
        self.request_string = ''
        
        self.update_request_params(request)
        
        # check for json param to decode
        if 'json' in self.params:
            try:
                # try to decode the value of json
                json_decoded = json.loads(self.params['json'])
                
                # update the request params with the decoded json values
                self.update_params(json_decoded)
                
                # delete the string from the request params
                del self.params['json']
            except ValueError:
                pass
        
        
        self.request = request
        self.request_string = request_string
        self.logger = logging.getLogger("nooga")
        self.parse(self.request_string)
    
    #Methods
    def update_request_params(self, request):
        
         # copy get params
        for key, value in request.GET.lists():
            if len(value) == 1:
                value = value[0]
            self.set_param(key, value)
        
        # copy post params
        for key, value in request.POST.lists():
            if len(value) == 1:
                value = value[0]
            self.set_param(key, value)
    
    def parse(self, request_string):
        #Process the request string
        route_list = request_string.strip("/").split("/")
        route_list_length = len(route_list)
        if route_list_length and len(route_list[0]):
            self.module = route_list[0]
            if route_list_length > 1:
                self.controller = route_list[1]
                if route_list_length > 2:
                    self.action = route_list[2]
            
        #Look for any extra key values in the url
        extra_parts = route_list[3:]
        self.args = extra_parts
        extra_params = {}
        for i in range(0, len(extra_parts), 2):
            if (i+1) < (len(extra_parts)):
                extra_params[extra_parts[i]] = extra_parts[i+1]
            elif len(extra_parts[i]):
                extra_params[extra_parts[i]] = False
        
        self.update_params(extra_params)
        return {
            "module": self.module,
            "controller": self.controller,
            "action": self.action
        }
    
    def get_url(self):
        return "/".join([self.module, self.controller, self.action])
    
    def set_params(self, params):
        self.params = params
        return self
    
    def update_params(self, params):
        self.params.update(params)
        return self
    
    def set_param(self, key, value=False):
        self.params[key] = value
        return self
    
    def get_param(self, key, default_value=None):
        if key in self.params:
            return self.params[key]
        return default_value
    
    def get_params(self):
        return self.params
    
    def get_module_name(self, name=False):
        if name is False:
            name = self.module
        parts = name.split('-')
        for i in range(len(parts)):
            parts[i] = parts[i].capitalize()
        return ''.join(parts)
    
    def get_controller_name(self, name=False):
        if name is False:
            name = self.controller
        parts = name.split('-')
        for i in range(len(parts)):
            parts[i] = parts[i].capitalize()
        return ''.join(parts)
    
    def get_action_name(self, name=False):
        if name is False:
            name = self.action
        name = name.lower()
        parts = name.split('-')
        action_name = '_'.join(parts)
        if (len(action_name)):
            return '%s_action' % action_name
        return False    