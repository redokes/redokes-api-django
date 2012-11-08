from redokes.controller.Crud import Crud

class ExternalApi(Crud):
    
    def init_defaults(self):
        Crud.init_defaults(self)
        self.allowed_params = {}