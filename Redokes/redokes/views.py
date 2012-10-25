from redokes.request.Parser import Parser
from redokes.controller import Front
from django.http import HttpResponse
from django.http import QueryDict

def route(request, request_string):
    if request.method == 'PUT' or request.method == 'DELETE':
        request.POST = QueryDict(request.raw_post_data)
    front_controller = Front.Front(request, request_string)
    return front_controller.run()
