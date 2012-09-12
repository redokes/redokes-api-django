from redokes.controller.Api import Api
from django.http import Http404
from django.conf import settings

class Crud(Api):
    
    def init_defaults(self):
        self.model_class = False
        self.lookup_class = False
        self.form_class = False
        self.primary_key = False
        self.model_instance = False
        self.lookup_instance = False
        self.access_module = None
        self.access_model = None
    
    def init(self):
        #Create the lookup class
        if self.lookup_class:
            self.lookup_instance = self.lookup_class(params=self.front_controller.request_parser.params)
            self.lookup_instance.front_controller = self.front_controller
            
        #Create the access based on the access_module and access_model
        """
        access = {
            "*": {
                "access": "admin"
            },
            "create_action": {
                "access": "article.add_article"
            },
            "read_action": {
                "access": "article.view_article"
            },
            "update_action": {
                "access": "article.change_article"
            },
            "delete_action": {
                "access": "article.delete_article"
            },
        }
        """
        if self.access is not None and self.access_module is not None and self.access_model is not None:
            action_permission_map = {
                'create': 'add',
                'read': 'view',
                'update': 'change',
                'delete': 'delete'
            }
            actions = ['create', 'read', 'update', 'delete']
            for action in actions:
                action_key = "{0}_action".format(action)
                if action_key in self.access:
                    continue
                self.access.update({
                    action_key: {
                        "access": "{0}.{1}_{2}".format(self.access_module, action_permission_map[action], self.access_model)
                    }
                })
            
        
        #call the parent
        return Api.init(self)
    
    def create_action(self):
        if not self.form_class or not self.model_class or not self.lookup_class:
            return
        
        #get response manager
        response_manager = self.front_controller.response_manager
        
        #Create the form
        form = self.form_class(self.parser.request.POST)
        form.request = self.parser.request
        if form.is_valid():
            form.save()
        else:
            for field, error in form.errors.iteritems():
                for message in error:
                    response_manager.add_error(message, field)
                    
        #Return the record if we had zero errors
        if not response_manager.any_errors():
            lookup = self.lookup_class({
                "id": form.instance.pk
            })
            self.set_response_param('record', lookup.get_row())
            self.set_response_param('id', form.instance.pk)
            
        return form.instance
            
                    
    def update_action(self):
        if not self.form_class:
            return
        
        id = int(self.get_request_param('id', 0))
        model = self.model_class.objects.get(pk=id)
        
        #get response manager
        response_manager = self.front_controller.response_manager
        
        #Create the form
        form = self.form_class(self.parser.request.POST, instance=model)
        form.request = self.parser.request
        if form.is_valid():
            form.save()
        else:
            for field, error in form.errors.iteritems():
                for message in error:
                    response_manager.add_error(message, field)
                    
        #Return the record if we had zero errors
        if not response_manager.any_errors():
            lookup = self.lookup_class({
                "id": form.instance.pk
            })
            self.set_response_param('record', lookup.get_row())
            self.set_response_param('id', form.instance.pk)
                    
        return form.instance
    
    def read_action(self):
        if self.lookup_instance:
            # run the lookup query to get the rows
            rows = self.lookup_instance.get_rows()
            query = self.lookup_instance.get_records().query
            # add records to the response
            self.set_response_param('num_records', len(rows))
            self.set_response_param('total_records', self.lookup_instance.get_count())
            self.set_response_param('current_page', self.lookup_instance.get_current_page())
            self.set_response_param('total_pages', self.lookup_instance.get_num_pages())
            self.set_response_param('records', rows)
            if settings.DEBUG:
                self.set_response_param('query', str(query))
                
            
    def delete_action(self):
        """
        Looks for the param of id.
        This can be a single digit or an array of digits
        """
        #Check if we have a model class
        if not self.model_class:
            return
        
        #Process the ids
        ids = self.get_request_param('id', [])
        if type(ids) is not list:
            ids = [ids]
            
        #Get the objects to delete
        delete_items = self.model_class.objects.filter(pk__in=ids)
        for delete_item in delete_items:
            delete_item.delete()
        
        self.set_response_param('records', ids)
