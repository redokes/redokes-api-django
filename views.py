from redokes.request.Parser import Parser
from redokes.controller import Front
from django.http import HttpResponse
import logging

def route(request, request_string):
    front_controller = Front.Front(request, request_string)
    return front_controller.run()
