from setuptools import setup, find_packages

setup(
    name = "Redokes",
    version = "0.1.5",
    packages = find_packages(),
    url = "https://github.com/redokes/redokes-api-django",
    description = "Redokes Framework.",
    include_package_data = True,
    install_requires = [
        "django>=1.4",
        "python-memcached",
        "django_extensions",
        "ipython",
        "beautifulsoup4",
        "jsonpickle",
        "python-dateutil",
    ],
    zip_safe = False
)

