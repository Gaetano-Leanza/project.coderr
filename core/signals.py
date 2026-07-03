"""
Signal handlers for the API application.

This module contains Django signals that automatically trigger specific 
actions when certain database events occur. Using signals helps decouple 
business logic from the models, keeping the codebase clean and modular.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a Profile instance whenever a new User is created.

    This signal receiver is triggered immediately after a `User` object is 
    saved to the database. If the 'created' flag is True (meaning it's a 
    brand new user and not just an update to an existing one), it generates 
    a linked `Profile` to store additional user-specific data.

    Args:
        sender (Model): The model class that sent the signal (in this case, User).
        instance (User): The actual instance of the User that was just saved.
        created (bool): True if a new record was created, False if an existing 
            record was simply updated.
        **kwargs: Additional keyword arguments passed by the signal dispatcher.
    """
    if created:
        # Create a matching profile pointing to the newly created user
        Profile.objects.create(user=instance)