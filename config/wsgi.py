"""
WSGI configuration for the Django project.

It exposes the WSGI (Web Server Gateway Interface) callable as a module-level
variable named ``application``. This is the standard interface that Python web
servers (like Gunicorn or uWSGI) use to interact with the Django application
in a production environment.

For more information on this file, see:
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Sets the default environment variable for Django's settings module.
# 'config.settings' points to the main configuration file of the project,
# allowing the WSGI server to know where your project settings are located.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initializes and exposes the WSGI application callable.
# Production web servers (e.g., Gunicorn, Apache, Nginx with uWSGI) will 
# look for this 'application' variable to serve incoming HTTP requests.
application = get_wsgi_application()