from django.db.models import Q
from redokes.database import Paging
from redokes.controller.Api import Api
from django.db.models import Avg
from django.db.models import Count
from django.db.models import Max

class Stats(Api):
    model = None
    date_field = None
    date_range = None
    start_date = None
    stop_date = None
    group_by = 'month'
    aggregate_field = None
    aggregate_function = 'count'
    extra = {}
    values = []
    order_by = ['-year']
    
    def init(self):
        # fields to apply
        self.extra = {}
        self.values = ['author', 'year']
        params = self.front_controller.request_parser.params
        fields = ['date_field', 'date_range', 'start_date', 'stop_date', 'group_by', 'aggregate_field', 'aggregate_function']
        for value in fields:
            if value in params:
                setattr(self, value, params[value])
                del params[value]
    
    def index_action(self):
        self.extra = {
            'day': 'DAY(published_at)',
            'month': 'MONTH(published_at)',
            'year': 'YEAR(published_at)',
        }
        
        aggregate_function = 'count'
        if self.aggregate_function == 'avg':
            aggregate_function = 'avg'
        rows = self.model.objects.extra(self.extra).values(*self.values).order_by(*self.order_by).annotate(value=Count(self.aggregate_field))
        print rows