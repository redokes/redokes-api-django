from redokes.request.Parser import Parser
from redokes.Response import Manager as ResponseManager
from django.http import Http404
from django.conf import settings

class Front(object):
    def __init__(self, request, request_string):
        self.request = None
        self.request_parser = None
        self.response_manager = None
        
        self.request = request
        self.init_request_parser(request, request_string)
        self.response_manager = ResponseManager()
        self.controller_instance = None
        
        
    def init_request_parser(self, request, request_string):
        self.request_parser = Parser(request, request_string)
        
    
    def run(self):
        #Build the import
        import_controller = self.request_parser.get_controller_name()
        import_path = '{0}.controller.{1}'.format(self.request_parser.module, import_controller)
        
        paths = [import_path] + ['{0}.{1}'.format(path, import_path) for path in settings.INSTALLED_APPS]
        
        #Try to import the controller
        controller = None
        
        for path in paths:
            try:
                controller = __import__(path, globals(), locals(), [import_controller], -1)
                self.request_parser.module = '.'.join(path.split('.')[:-2])
                self.controller_instance = getattr(controller, import_controller)(self)
            except:
                pass
#                print 'did not find {0}'.format(path)
            if self.controller_instance is not None:
                continue
        
        if controller is None:
            #Raise a 404 if the controller is not found
            print import_path + " - controller class not found"
            raise Http404
        
        #Run the action
        self.controller_instance.run()
        return self.controller_instance.send_headers()
