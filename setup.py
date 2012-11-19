from setuptools import setup, find_packages

setup(
    name = "Redokes",
    version = "0.1.3",
    packages = find_packages(),
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

