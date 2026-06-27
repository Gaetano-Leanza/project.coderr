"""
Custom permissions for the API application.

This module defines custom authorization classes for the Django REST Framework.
These classes enforce role-based access control (e.g., distinguishing between 
'customer' and 'business' users) and object-level permissions (e.g., ensuring 
users can only edit their own data or orders they participate in).
"""

from rest_framework import permissions


class IsOwnerProfile(permissions.BasePermission):
    """
    Object-level permission to only allow the owner of a profile to edit it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Checks if the requesting user is the owner of the profile object.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The Profile object being accessed.

        Returns:
            bool: True if the user owns the profile, False otherwise.
        """
        return obj.user == request.user


class IsBusinessProfile(permissions.BasePermission):
    """
    Global permission to only allow 'business' type users to access a view.
    
    Typically used to restrict offer creation to business accounts only.
    """
    message = "Nur User vom type 'business' dürfen Angebote erstellen."

    def has_permission(self, request, view):
        """
        Checks if the user is authenticated and possesses a business profile.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.

        Returns:
            bool: True if the user is an authenticated business, False otherwise.
        """
        if not request.user.is_authenticated:
            return False

        return hasattr(request.user, 'profile') and request.user.profile.type == 'business'


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to allow read-only access to anyone, but restrict 
    write/delete operations to the object's owner.
    """

    def has_object_permission(self, request, view, obj):
        """
        Allows safe methods (GET, HEAD, OPTIONS) for anyone, but requires
        ownership (obj.user) for write/delete operations.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The object being accessed (must have a 'user' attribute).

        Returns:
            bool: True if authorized, False otherwise.
        """
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsCustomer(permissions.BasePermission):
    """
    Global permission to only allow 'customer' type users to access a view.
    
    Typically used to restrict order creation and review posting to customers.
    """
    message = "Benutzer hat keine Berechtigung, z.B. weil nicht vom typ 'customer'."

    def has_permission(self, request, view):
        """
        Checks if the user is authenticated and possesses a customer profile.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.

        Returns:
            bool: True if the user is an authenticated customer, False otherwise.
        """
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.type == 'customer'
        except AttributeError:
            return False


class IsOrderParticipant(permissions.BasePermission):
    """
    Object-level permission to only allow participants of an order to view/edit it.
    """
    message = "Benutzer hat keine Berechtigung, diese Bestellung zu aktualisieren."

    def has_object_permission(self, request, view, obj):
        """
        Checks if the requesting user is either the customer or the business 
        associated with the specific order.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The Order object being accessed.

        Returns:
            bool: True if the user is a participant, False otherwise.
        """
        return obj.customer_user == request.user or obj.business_user == request.user


class IsReviewCreator(permissions.BasePermission):
    """
    Object-level permission to only allow the original creator of a review to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Checks if the requesting user matches the reviewer of the object.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The Review object being accessed.

        Returns:
            bool: True if the user created the review, False otherwise.
        """
        return obj.reviewer == request.user