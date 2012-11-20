redokes-api-django
==================

A Django framework that allows for easy url routing and API creation following the Redokes WAIS (Works And Isnt Shitty) API guidelines

# Installation

 - Add git+https://github.com/wesokes/redokes-api-django.git to your requirements.txt or setup.py
 - Add redokes as an installed app
 - If you want a default index page add the redokes.index module
 - Add the following to the end of your urls.py, this will catch and forward any urls that arent caught by anything else in the application

        urlpatterns.append(
            url(r'^(.*?)$', 'redokes.views.route')
        )

# Routing System

- The routing system works off the url that the user is trying to access. Its broken down into three levels
  - Module, the python module associated with this url
  - Controller, the controller of this module that will handle all actions associated with this module 
  - Action, the action to perform on the controller, the action is used to get any data needed to be passed back to the user or template
- The basic url pattern is module/controller/action

# Controllers

- Create a new application, for example we will make an "index" application. This will represent the entry point of our application
- Inside of the new application directory create a "controllers" directory. index/controllers
- Inside of controllers directory create a new controller, ControllerName.py, for our example. index/controllers/Index.py
- At this point we have our module name "index", our controller name "index", now we need to add any actions that we want for this module and controller.
- When the router loads an action controller it looks for the a method called {actionName_action}. For example index/index/index would route to the index module, create an instance of the index controller, and try to call a method named index_action.
- Index.py

        from redokes.controller.Action import Action
        class Index(Action):
            def index_action(self):
                pass

# Auto Templates

    