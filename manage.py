#!/usr/bin/env python
"""
Entry point for Django's command-line utility.

This script is the primary tool for executing administrative tasks in Django,
such as starting the development server (`runserver`), creating database
migrations (`makemigrations`), or creating superusers.
"""
import os
import sys


def main():
    """
    Executes administrative Django tasks via the command line.

    Sets the environment variable for the Django settings and subsequently
    executes the requested command-line argument.

    Raises:
        ImportError: If Django cannot be found in the current Python environment
            (e.g., if the virtual environment has not been activated).
    """
    # Tells Django where to find the configuration file (settings.py).
    # Note: 'config.settings' must exactly match your project structure.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    try:
        # Attempts to load the core function for executing console commands.
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # Catches the error and provides a helpful error message if the 
        # virtual environment (venv) was not activated.
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
        
    # Passes the typed console arguments (e.g., ['manage.py', 'runserver'])
    # to Django so the corresponding command can be executed.
    execute_from_command_line(sys.argv)


# This block ensures that main() is only executed when the script is run 
# directly (e.g., via 'python manage.py ...') and not when imported by another file.
if __name__ == '__main__':
    main()