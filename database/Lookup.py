import json
from django.db.models import Q
from redokes.database import Paging
import redokes.util
from math import ceil

class Lookup(object):
    util = redokes.util
    
    def init_defaults(self):
        self.params = {}
        self.sort = []
        self.filters = []
        self.exclude = []
        
        self.start = 0
        self.limit = 10
        self.page = 0
        
        self.model = None
        
        self.num_records = 0
        self.total_records = 0
        
        self.fields = []
        self.related_tables = []
        self.search_fields = []
        self.query_set = None
        self.rows = []
        self.records = None
        self.front_controller = None
    
    def __init__(self, params={}, *args, **kwargs):
        self.init_defaults()
        
        #Set the params
        self.params = params
        
        #Apply the kwargs
        redokes.util.apply_config(self, kwargs)
        
        #Get the limit
        if "limit" in self.params:
            self.limit = int(self.params["limit"])
            if self.limit < 1:
                self.limit = 1
            del self.params['limit']
            
        #Get the start
        if "start" in self.params:
            self.start = int(self.params["start"])
            if self.start < 0:
                self.start = 0
            del self.params['start']
        
        #Get the page
        if "page" in self.params:
            self.page = int(self.params["page"])
            if self.page < 1:
                self.page = 1
            self.start = (self.page - 1) * self.limit
            del self.params['page']
        
        #Get the sort
        if "sort" in self.params:
            if type(self.params["sort"]) is list:
                self.sort = self.params["sort"]
            else:
                try:
                    self.sort = json.loads(self.params["sort"])
                except:
                    self.sort = []
            del self.params['sort']
        
        #Get the filters
        if "filter" in self.params:
            try:
                self.filters = json.loads(self.params["filter"])
            except:
                self.filters = []
            del self.params['filter']
        
        
        # auto set filters from params
        for key, value in self.params.iteritems():
            self.add_filter(key, value)
    
    def get_query_set(self, fields=None):
        self.query_set = self.model.objects.order_by(
            *self.get_order()
        ).filter(
            *self.process_filters()
        ).exclude(
            *self.exclude
        ).select_related(
            *self.related_tables
        ).distinct()
        
        if fields is not None:
            self.query_set = self.query_set.values(
                *fields
            )
        
        return self.query_set
    
    def get_order(self):
        #Compute the order, [property: direction]
        order = []
        for sorter in self.sort:
            sort_string = sorter['property']
            if sorter['direction'].lower() == "desc":
                sort_string = "-" + sort_string
            order.append(sort_string)
        return order
    
    def process_filters(self):
        filter_objects = []
        for filter_item in self.filters:
            prop = filter_item['property']
            val = filter_item['value']
            if isinstance(val, str) and not len(val):
                continue
            
            #Check if the method exists
            filter_method_name = self.get_method_name(prop, 'filter')
            if hasattr(self, filter_method_name):
                filter_method = getattr(self, filter_method_name)
                if filter_method:
                    return_filter = filter_method(val)
                    if type(return_filter) is tuple:
                        for filter in return_filter:
                            if filter is not None:
                                filter_objects.append(filter)
                    elif return_filter is not None:
                        filter_objects.append(return_filter)
                
        return filter_objects
    
    def get_records(self, start=0, limit=0):
        start = start or self.start
        limit = limit or self.limit
        stop = start + limit
        
        self.total_records = self.get_query_set().count()
        
        # check if a certain page needs to be returned
        if self.page:
            self.records = Paging.get_paged_set(self.get_query_set(), limit=self.limit, page=self.page)
        else:
            self.records = self.query_set[start:stop]
        
        return self.records
    
    def get_num_records(self):
        return len(self.rows)
    
    def get_rows(self):
        self.rows = self.get_records().values(*self.fields)
        self.format_rows()
        return self.rows
    
    def format_rows(self):
        for row in self.rows:
            row = self.format_row(row)
    
    def get_row(self):
        limit = self.start + 1
        self.get_query_set(self.fields)
        rows = list(self.get_records(self.start, limit))
        
        #Run the rows through the formatter
        formatted_rows = []
        for row in rows:
            formatted_rows.append(self.format_row(row))
            
        #Return the formatted rows
        return formatted_rows[0]
    
    def format_row(self, row):
        """
        Override this method to add additional fields to the row.
        Or do custom rendering of a field. Only used when get_row or
        get_rows is called.
        """
        return row
    
    def get_total_records(self):
        return self.total_records
    
    def get_current_page(self):
        if hasattr(self.get_query_set(), 'paginator'):
            return self.query_set.number
        elif not self.page and not self.start:
            return 1
        elif self.page:
            return self.page
        else:
            return None
    
    def get_num_pages(self):
        if hasattr(self.query_set, 'paginator'):
            return self.query_set.paginator.num_pages
        else:
            pass
        return ceil(self.get_total_records() / float(self.limit))
    
    def add_sorter(self, property, direction):
        self.sort.append({
            'property': property,
            'direction': direction
        })
        
    def add_filter(self, property, value, *args, **kwargs):
        self.filters.append({
            'property': property,
            'value': value
        })
        
    def set_filter(self, property, value):
        found = False
        for filter in self.filters:
            if filter["property"] == property:
                filter["property"] = value
                found = True
                break
        if not found:
            self.add_filter(property, value)
            
    def get_method_name(self, name, prefix=''):
        method = prefix
        name = name.lower()
        name_parts = name.split("_")
        for name_part in name_parts:
            method = method + "_" + name_part.lower()
        return method
    
    """""""""""""""""""""""""""""""""
    Default Filters
    """""""""""""""""""""""""""""""""
    def filter_query(self, value):
        if not len(value):
            return None
        
        #loop through each search field
        return_filter = None
        for search_field in self.search_fields:
            current_filter = Q(**{ "{0}__istartswith".format(search_field): value})
            if return_filter is not None:
                return_filter = return_filter | current_filter
            else:
                return_filter = current_filter
        
        return return_filter
    
    def filter_id(self, value):
        return Q(pk=value)
    
