"""
ASGI configuration for the Django project.

It exposes the ASGI (Asynchronous Server Gateway Interface) callable as a
module-level variable named ``application``. This interface enables Django
to handle asynchronous web requests (such as WebSockets and long-polling) 
and is utilized by ASGI-compatible servers like Daphne or Uvicorn.

For more information on this file, see:
https://docs.djangoproject.com/en/6.0/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# Sets the default environment variable for Django's settings module.
# This allows the ASGI server to locate and load your project's configuration.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initializes and exposes the ASGI application callable.
# Production ASGI servers will look for this 'application' variable 
# to serve incoming asynchronous HTTP and WebSocket requests.
application = get_asgi_application()