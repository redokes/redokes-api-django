from django.db.models import Q
from redokes.controller.Api import Api
from django.db.models import Avg
from django.db.models import Count
from django.db.models import Max

class Stats(Api):
    
    def init_defaults(self):
        Api.init_defaults(self)
        self.access = None
        self.model = None
        self.model_class = None
        self.stats_class = None
        self.stats_instance = None
        
        self.entity_class = None
        self.entity_query_set = None
        self.entity_query_set = None
        self.entity_values = []
        self.entity_excludes = {}
        self.entity_legend_prefix = ''
        self.entity_legend_map_field = ''
        self.entity_format = ''
        self.entity_formatters = []
        
    def init(self):
        # Create the stats class
        if self.stats_class:
            self.stats_instance = self.stats_class(params=self.front_controller.request_parser.params)
        if self.entity_class:
            self.entity_query_set = self.entity_class.objects.values(*self.entity_values).exclude(**self.entity_excludes).distinct()
    
    def read_action(self):
        # Get the main stats
        for entity in self.entity_query_set:
            format_data = [entity[data] for data in self.entity_formatters]
            self.stats_instance.legend_map['{0}__{1}'.format(self.entity_legend_prefix, entity[self.entity_legend_map_field])] = self.entity_format.format(*format_data)
#        stats.filters.append(Q(reporter__id=4))
        
        # Add records to the response
        rows = self.stats_instance.get_rows()
        self.set_response_param('total_records', len(rows))
        self.set_response_param('records', rows)
        self.set_response_param('legend_map', self.stats_instance.legend_map)
        self.set_response_param('x_label', self.stats_instance.x_label)
        self.set_response_param('y_label', self.stats_instance.y_label)