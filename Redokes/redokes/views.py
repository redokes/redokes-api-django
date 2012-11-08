from redokes.request.Parser import Parser
from redokes.controller import Front
from django.http import HttpResponse
from django.http import QueryDict

def route(request, request_string):
    XS_SHARING_ALLOWED_ORIGINS = '*'
    XS_SHARING_ALLOWED_METHODS = ['POST','GET','OPTIONS', 'PUT', 'DELETE']
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['access-control-allow-credentials'] = 'true'
        response['access-control-allow-origin']  = '*'
        response['access-control-allow-headers'] = 'x-requested-with'
        return response
    
    if request.method == 'PUT' or request.method == 'DELETE':
        request.POST = QueryDict(request.raw_post_data)
    front_controller = Front.Front(request, request_string)
    response = front_controller.run()
    response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS 
    response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )
    return response
