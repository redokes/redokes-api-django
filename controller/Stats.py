from django.db.models import Q
from redokes.database import Paging
from redokes.controller.Api import Api
from django.db.models import Avg
from django.db.models import Count
from django.db.models import Max

class Stats(Api):
    
    def init_defaults(self):
        Api.init_defaults(self)
        self.model = None
        self.date_field = None
        self.date_range = None
        self.start_date = None
        self.stop_date = None
        self.group_by = 'month'
        self.aggregate_field = None
        self.aggregate_function = 'count'
        self.extra = {}
        self.values = []
        self.order_by = ['-year']
    
#    def init(self):
#        # fields to apply
#        self.extra = {}
#        self.values = ['author', 'year']
#        params = self.front_controller.request_parser.params
#        fields = ['date_field', 'date_range', 'start_date', 'stop_date', 'group_by', 'aggregate_field', 'aggregate_function']
#        for value in fields:
#            if value in params:
#                setattr(self, value, params[value])
#                del params[value]
    
    def index_action(self):
        print 'wow index'
#        self.extra = {
#            'day': 'DAY(published_at)',
#            'month': 'MONTH(published_at)',
#            'year': 'YEAR(published_at)',
#        }
#        
#        aggregate_function = 'count'
#        if self.aggregate_function == 'avg':
#            aggregate_function = 'avg'
#        rows = self.model.objects.extra(self.extra).values(*self.values).order_by(*self.order_by).annotate(value=Count(self.aggregate_field))
#        print rows