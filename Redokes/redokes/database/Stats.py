import json
from django.db.models import Q
import redokes.util
import datetime
from dateutil.relativedelta import *
from django.db.models import Count, Avg, Max

now = datetime.datetime.now()
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
next_week = today + datetime.timedelta(weeks=1)
last_week = today - datetime.timedelta(weeks=1)
next_month = today + relativedelta(months=1)
last_month = today - relativedelta(months=1)
next_year = today + relativedelta(years=1)
last_year = today - relativedelta(years=1)
delta = next_year - today
datetime.datetime.strptime("2012/10/24", "%Y/%m/%d")

group_names = (
    'year',
    'month',
    'day',
    'hour',
    'minute',
    'second',
    'week',
)

default_group_names = (
    'year',
    'month',
    'day',
    'hour',
    'minute',
    'second',
)

week_group_names = (
    'year',
    'week',
)

class Stats(object):
    util = redokes.util
    
    def init_defaults(self):
        self.params = {}
        self.model = None
        
#        self.model = None
        
        self.date_field = None
        self.group_by = 'month'
        self.start_date = None
        self.end_date = last_year
        self.date_range = None
        
        self.group_names = []
        self.extra = {}
        self.select = {}
        self.values = []
        self.order_by = []
        self.aggregates = []
        self.filter = {}
        
#        self.num_records = 0
#        self.total_records = 0
        
        self.query_set = None
        self.rows = []
        self.records = None
        
        
    
    def __init__(self, model=None, date_field=None, params={}, *args, **kwargs):
        self.init_defaults()
        
        self.model = model
        
        #Set the params
        self.params = params
        
        #Apply the kwargs
        redokes.util.apply_config(self, kwargs)
        
        # Check date field
        self.date_field = date_field
        
        # Check group by
        if 'group_by' in self.params:
            group_by = self.params['group_by']
            if group_by in self.group_names:
                self.group_by = group_by
            del self.params['group_by']
        
        # Set group names
        if self.group_by == 'week':
            self.group_names = week_group_names
        else:
            self.group_names = default_group_names
        
        # Build grouping data
        for group_name in self.group_names:
            self.select[group_name] = 'extract({0} from {1})'.format(group_name, self.date_field)
            self.values.append(group_name)
            self.order_by.append('-{0}'.format(group_name))
            if group_name == self.group_by:
                break
        
        # Set the extra select data
        self.extra = {
            'select': self.select
        }
        
        # Set the aggregates
        self.aggregates = {
            'num_records': Count('id'),
            'average_priority': Avg('priority__level'),
            'average_difficulty': Avg('difficulty__value'),
        }
        
        # Check start date
        if 'start_date' in self.params:
            try:
                self.start_date = datetime.datetime.strptime(self.params['start_date'], "%Y/%m/%d")
            except Exception, e:
                pass
            del self.params['start_date']
        
        # Check end date
        if 'end_date' in self.params:
            try:
                end_date = datetime.datetime.strptime(self.params['end_date'], "%Y/%m/%d")
                if end_date > self.start_date:
                    self.end_date = end_date
            except Exception, e:
                pass
            del self.params['end_date']
        
        # Check date range
        if 'date_range' in self.params:
            date_range = self.params['date_range']
            if date_range in group_names:
                if date_range == 'year':
                    self.end_date = self.start_date - relativedelta(years=1)
                elif date_range == 'month':
                    self.end_date = self.start_date - relativedelta(months=1)
                elif date_range == 'week':
                    self.end_date = self.start_date - datetime.timedelta(weeks=1)
                elif date_range == 'day':
                    self.end_date = self.start_date - datetime.timedelta(days=1)
        
        # Set the dange range in the filter
        self.filter = {}
        if not self.start_date:
            self.start_date = today
        if not self.end_date:
            self.end_date = last_year
        self.filter['{0}__range'.format(self.date_field)] = (self.end_date, self.start_date)
        
    
    def get_query_set(self):
        self.query_set = self.model.objects.extra(
            **self.extra
        ).values(
            *self.values
        ).annotate(
            **self.aggregates
        ).filter(
            **self.filter
        ).order_by(
            *self.order_by
        )
        
        return self.query_set
    
    def get_records(self):
        self.records = self.get_query_set()
        return self.records
    
    def get_rows(self):
        self.rows = [record for record in self.get_records()]
        self.format_rows()
        return self.rows
    
    def format_rows(self):
        for row in self.rows:
            row = self.format_row(row)
    
    def format_row(self, row):
        """
        Override this method to add additional fields to the row.
        Or do custom rendering of a field. Only used when get_row or
        get_rows is called.
        """
        return row
    
