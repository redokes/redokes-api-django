import json
from django.db.models import Q
import redokes.util
import datetime
from dateutil.relativedelta import *
from django.db.models import Count, Avg, Max

now = datetime.datetime.now()
today = datetime.datetime.today()
tomorrow = today + datetime.timedelta(days=1)
next_week = today + datetime.timedelta(weeks=1)
last_week = today - datetime.timedelta(weeks=1)
next_month = today + relativedelta(months=1)
last_month = today - relativedelta(months=1)
next_year = today + relativedelta(years=1)
last_year = today - relativedelta(years=1)
delta = next_year - today
datetime.datetime.strptime("2012/10/24", "%Y/%m/%d")

all_group_names = (
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

date_display_formats = {
    'year': '%Y',
    'month': '%B %Y',
    'day': '%m-%d-%Y',
    'hour': '%i:%m %p',
    'minute': '%i:%m:%S %p',
}

x_labels = {
    'year': 'Years',
    'month': 'Months',
    'day': 'Days',
    'hour': 'Hours',
    'minute': 'Minutes',
}

class Stats(object):
    util = redokes.util
    
    def init_defaults(self):
        self.params = {}
        self.model = None
        
#        self.model = None
        
        self.date_field = None
        self.group_by = None
        self.start_date = last_year
        self.end_date = today
        self.date_range = 'month'
        
        self.group_names = []
        self.extra = {}
        self.select = {}
        self.where = []
        self.values = []
        self.date_values = []
        self.order_by = []
        
        self.aggregates = {}
        self.aggregate_function = Count
        self.aggregate_field = 'id'
        self.aggregate_name = 'id__count'
        
        self.filters = []
        
        self.legend_map = {}
        self.legend_map_prefix = ''
        self.legend_map_field = None
        
        self.x_label = 'x Axis'
        self.y_label = 'y Axis'
        
#        self.num_records = 0
#        self.total_records = 0
        
        self.query_set = None
        self.rows = []
        self.records = None
        
        
    
    def __init__(self, params={}, *args, **kwargs):
        self.init_defaults()
        
        #Apply the kwargs
        redokes.util.apply_config(self, kwargs)
        
        # Set the params
        self.params = params.copy()
        
        # The most common param will be date_range
        # default is month
        if 'date_range' in self.params:
            if self.params['date_range'] in all_group_names:
                self.date_range = self.params['date_range']
            del self.params['date_range']
        
        if self.date_range == 'year':
            self.start_date = self.end_date - relativedelta(years=1)
        elif self.date_range == 'month':
            self.start_date = self.end_date - relativedelta(months=1)
        elif self.date_range == 'week':
            self.start_date = self.end_date - datetime.timedelta(weeks=1)
        elif self.date_range == 'day':
            self.start_date = self.end_date - datetime.timedelta(days=1)
        
        # Set the default group_by to the
        # next date grouping after date_range
        default_group_by = None
        last_group_name = None
        for group_name in all_group_names:
            if last_group_name == self.date_range:
                default_group_by = group_name
                break
            last_group_name = group_name
        
        # Check group by
        if 'group_by' in self.params:
            self.set_group_by(self.params['group_by'])
            del self.params['group_by']
        else:
            self.set_group_by(default_group_by)
        
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
        
        # Set the aggregates
        self.aggregates = {}
        self.aggregates[self.aggregate_name] = self.aggregate_function(self.aggregate_field)
        
        # Set the dange range in the filter
        if not self.start_date:
            self.start_date = last_year
        if not self.end_date:
            self.end_date = today
        
        self.where.append('{0}.{1} BETWEEN \'{2}\' AND \'{3}\''.format(self.model._meta.db_table, self.date_field, self.start_date, self.end_date))
         
#        self.filter['{0}__range'.format(self.date_field)] = (self.start_date, self.end_date)
        
        # Set the extra select data
        self.extra = {
            'select': self.select,
            'where': self.where,
        }
        
    def set_group_by(self, group_by):
        if group_by in all_group_names:
            self.group_by = group_by
        
        # Set group names
        if self.group_by == 'week':
            self.group_names = week_group_names
        else:
            self.group_names = default_group_names
        
        # Build grouping data
        self.select = {}
#        self.values = []
        self.date_values = []
        self.order_by = []
        for group_name in self.group_names:
            self.select[group_name] = 'CAST(extract({0} from {1}) as INT)'.format(group_name, self.date_field)
            self.date_values.append(group_name)
            self.order_by.append('{0}'.format(group_name))
            if group_name == self.group_by:
                break
        
        self.x_label = x_labels[self.group_by]
         
    
    def get_query_set(self):
        self.query_set = self.model.objects.extra(
            **self.extra
        ).values(
            *(self.date_values + self.values)
        ).annotate(
            **self.aggregates
        ).filter(
            *self.filters
        ).order_by(
            *self.order_by
        )
        
        return self.query_set
    
    def get_records(self):
        self.records = self.get_query_set()
        return self.records
    
    def get_rows(self):
        self.rows = [record for record in self.get_records()]
#        self.populate_missing_rows()
        self.format_rows()
        self.combine_rows();
        return self.rows
    
    def populate_missing_rows(self):
        # Iterate through the items based on the grouping
        # to fill in any missing records
        
        current_date = self.end_date
        grouping = {}
        grouping['{0}s'.format(self.group_by)] = 1
        new_rows = []
        
        # right now sort is always descending so iterate backwards
        num_expected = (self.end_date - self.start_date).days
        expected_index = 0
        existing_index = 0
        empty_row = {}
        for key in self.aggregates.keys():
            empty_row[key] = 0
        
        while expected_index < num_expected:
            # Check if the first row exists
            if self.rows[existing_index]['year'] == current_date.year and self.rows[existing_index]['month'] == current_date.month and self.rows[existing_index]['day'] == current_date.day:
                new_rows.append(self.rows[existing_index])
                existing_index += 1
            else:
                filler_row = empty_row.copy()
                filler_row.update({
                    'year':current_date.year,
                    'month':current_date.month,
                    'day':current_date.day,
                })
                new_rows.append(filler_row)
            current_date -= relativedelta(**grouping)
            expected_index += 1
        self.rows = new_rows
    
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
    
    def combine_rows(self):
        
        # create empty rows
        new_rows = []
        required_fields = []
        
        for key in self.aggregates.keys():
            required_fields.append(key)
        for value in self.date_values:
            required_fields.append(value)
        
        current_date = self.start_date
        grouping = {}
        grouping['{0}s'.format(self.group_by)] = 1
        
        while current_date <= self.end_date:
            current_date += relativedelta(**grouping)
            row = {}
            for key in self.date_values:
                row[key] = getattr(current_date, key)
            for key in self.aggregates.keys():
                row[key] = 0
            
            # Add date display
            row['date_display'] = current_date.strftime(date_display_formats[self.group_by])
            
            new_rows.append(row)
        
        for new_row in new_rows:
            for row in self.rows:
                found_record = True
                for date_value in self.date_values:
                    if row[date_value] != new_row[date_value]:
                        found_record = False
                if found_record:
                    for aggregate_name in self.aggregates.keys():
                        new_row['{0}__{1}'.format(self.legend_map_prefix, row[self.legend_map_field])] = row[aggregate_name]
                    
        
        # fill in empty rows
        for new_row in new_rows:
            for legend_key in self.legend_map:
                if legend_key not in new_row:
                    new_row[legend_key] = 0
        
        self.rows = new_rows
        
        return
        
        
        grouping = {}
        grouping['{0}s'.format(self.group_by)] = 1
        num_expected = (self.end_date - self.start_date).days
        expected_index = 0
        existing_index = 0
        empty_row = {}
        
        while expected_index < num_expected:
            # Check if the first row exists
            if self.rows[existing_index]['year'] == current_date.year and self.rows[existing_index]['month'] == current_date.month and self.rows[existing_index]['day'] == current_date.day:
                new_rows.append(self.rows[existing_index])
                existing_index += 1
            else:
                filler_row = empty_row.copy()
                filler_row.update({
                    'year':current_date.year,
                    'month':current_date.month,
                    'day':current_date.day,
                })
                new_rows.append(filler_row)
            current_date -= relativedelta(**grouping)
            expected_index += 1
        self.rows = new_rows
        
        fields_to_keep = ['year', 'month']
        real_rows = []
        for row in self.rows:
            for field in fields_to_keep:
                real_rows[field]
            
                
