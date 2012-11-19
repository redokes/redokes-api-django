from distutils.core import setup

setup(
    name = "Redokes",
    version = "0.1.3",
    packages = [
        "redokes",
        "redokes.controller",
        "redokes.database",
        "redokes.request",
        "redokes.templatetags"
    ],
    url = "https://github.com/redokes/redokes-api-django",
    description = "Redokes Framework.",
    install_requires = [
        "django>=1.4",
        "python-memcached",
        "django_extensions",
        "ipython",
        "beautifulsoup4",
        "jsonpickle",
        "python-dateutil",
    ]
)

