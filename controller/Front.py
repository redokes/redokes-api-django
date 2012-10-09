from redokes.request.Parser import Parser
from redokes.Response import Manager as ResponseManager
from django.http import Http404

class Front(object):
    def __init__(self, request, request_string):
        self.request = None
        self.request_parser = None
        self.response_manager = None
        
        self.request = request
        self.init_request_parser(request, request_string)
        self.response_manager = ResponseManager()
        
        
    def init_request_parser(self, request, request_string):
        self.request_parser = Parser(request, request_string)
        
    
    def run(self):
         #Build the import
        import_controller = self.request_parser.get_controller_name()
        import_path = self.request_parser.module + ".controller." + import_controller
        #Try to import the controller
        controller = None
        try:
            controller = __import__(import_path, globals(), locals(), [import_controller], -1)
            self.controller_instance = getattr(controller, import_controller)(self)
        except:
            #Raise a 404 if the controller is not found
            print import_path + " - controller class not found"
            raise Http404
        
        #Run the action
        self.controller_instance.run()
        return self.controller_instance.send_headers()
