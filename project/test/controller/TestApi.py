from redokes.controller.Api import Api

class TestApi(Api):
    
    def init_defaults(self):
        Api.init_defaults(self)
        self.access = None
    
    def index_action(self):
        
        return
