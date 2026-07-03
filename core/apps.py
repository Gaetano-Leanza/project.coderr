"""
Application configuration for the API app.

This module contains the Django application configuration. It is used 
by the framework to register the app, manage its metadata, and execute 
startup code (such as importing signal handlers).
"""

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """
    Configuration class for the 'api' application.
    
    Django uses this class to identify the application and handle its 
    initialization. If you need to run specific code when the app starts 
    (e.g., overriding the `ready()` method to connect signal receivers), 
    this is the place to do it.
    """
    # The full Python path to the application.
    name = 'core'