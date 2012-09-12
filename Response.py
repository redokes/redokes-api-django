from django.http import HttpResponse, HttpRequest
from django.http import Http404
import json

class Manager(object):
    def __init__(self):
        self.errors = []
        self.messages = []
        self.redirect = False
        self.values = {}
    
    def add_message(self, str):
        message = Message({
            'msg': str,
        })
        self.messages.append(message)
    
    def add_error(self, str, field_name=False):
        message = Message({
            'msg': str,
            'id': field_name,
        })
        self.errors.append(message)
    
    def any_errors(self):
        if len(self.errors):
            return True
        return False
    
    def json_handler(self, obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        else:
            raise TypeError, 'Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj))
    
    def get_response_string(self):
        # prepare response data
        if len(self.errors):
            self.values['success'] = False
        else:
            self.values['success'] = True
        self.values['messages'] = self.get_as_dict(self.messages)
        self.values['errors'] = self.get_as_dict(self.errors)
        
        #build error string as list
        error_string = '<div class="form-messages form-errors"><ul>'
        errors = self.get_as_dict(self.errors)
        for error in errors:
            error_string += '<li><strong>{0}</strong> - {1}</li>'.format(error['id'], error['msg'])
        error_string += '</ul></div>'
        self.values['error_string'] = error_string
        
        """
        // build message string as list
        $msgStr = '';
        $messages = $responseManager->getMessages();
        $numMessages = count($messages);
        if ($numMessages == 1) {
            $msgStr = $messages[0]->getMsg();
        }
        else if ($numMessages > 1) {
            $msgStr = '<div class="form-messages"><ul>';
            for ($i = 0; $i < $numMessages; $i++) {
                $message = $messages[$i];
                $msgStr .= '<li field="' . $message->getId() . '">' . $message->getMsg() . '</li>';
            }
            $msgStr .= '</ul></div>';
        }
        """
        
        return json.dumps(self.values, default=self.json_handler)
    
    def get_as_dict(self, messages):
        values = []
        for message in messages:
            values.append(message.to_dict())
        return values
    
    def has_param(self, key):
        return key in self.values
    
    def set_param(self, key, value=None):
        self.values[key] = value
        return self
    
    def set_params(self, params):
        self.values.update(params)
    
    def update_params(self, params):
        self.values.update(params)
        return self
    
    def get_param(self, key, default_value=None):
        if key in self.values:
            return self.values[key]
        return default_value
    
    def get_params(self):
        return self.values
    
    def push_param(self, key):
        pass
    
    def get_values(self, key):
        return self.values
    
            
    
class Message():
    
    def __init__(self, config={}):
        self.hash_name = ''
        self.id = ''
        self.msg = ''
        self.form_id = ''
        for i in config:
            if hasattr(self, i):
                setattr(self, i, config[i])
    
    def to_dict(self):
        return {
            'hash_name': self.hash_name,
            'id': self.id,
            'msg': self.msg,
            'form_id': self.form_id,
        }