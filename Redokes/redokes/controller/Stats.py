from django.db.models import Q
from redokes.database import Paging
from redokes.controller.Api import Api
from django.db.models import Avg
from django.db.models import Count
from django.db.models import Max

class Stats(Api):
    
    def init_defaults(self):
        Api.init_defaults(self)
        self.access = None
        self.model = None
        
    
    