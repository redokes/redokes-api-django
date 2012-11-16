redokes-api-django
==================

A Django framework that allows for easy url routing and API creation following the Redokes WAIS (Works And Isnt Shitty) API guidelines

# Installation

 - Add git+https://github.com/wesokes/redokes-api-django.git to your requirements.txt or setup.py
 - Add redokes as an installed app
 - Add the following to the end of your urls.py

        urlpatterns.append(
            url(r'^(.*?)$', 'redokes.views.route')
        )

# Usage for templating

- Create a new application
- Inside of the new application directory create a "controllers" directory
- Inside of controllers directory create a new controller, ControllerName.py
- ControllerName.py

    