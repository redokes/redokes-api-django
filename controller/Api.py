from redokes.controller.Action import Action
from django.http import HttpResponse
from django.forms.models import model_to_dict
import redokes.util

class Api(Action):
    def init_defaults(self):
        Action.init_defaults(self)
        self.auto_template = False,
        self.output_type = 'json',
        self.access = {
            '*': {
                'access': 'admin'
            }
        }    
    
    def get_output_403(self):
        self.add_error("You do not have permission to complete this action - {0}".format(self.parser.request_string))
        return self.get_output_json()
    
    def get_output_json(self):
        return HttpResponse(self.front_controller.response_manager.get_response_string(), mimetype="application/json")
    
    def convert_models(self, models):
        records = []
        for model in models:
            records.append(model_to_dict(model))
        return records
    
    def add_message(self, str):
        self.front_controller.response_manager.add_message(str)
        
    def add_error(self, message, field=''):
        self.front_controller.response_manager.add_error(message, field)

