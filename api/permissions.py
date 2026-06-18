from rest_framework import permissions


class IsOwnerProfile(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        return obj.user == request.user


class IsBusinessProfile(permissions.BasePermission):
    message = "Nur User vom type 'business' dürfen Angebote erstellen."

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return hasattr(request.user, 'profile') and request.user.profile.type == 'business'


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.user == request.user


class IsCustomer(permissions.BasePermission):
    message = "Benutzer hat keine Berechtigung, z.B. weil nicht vom typ 'customer'."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.profile.type == 'customer'
        except AttributeError:
            return False


class IsOrderParticipant(permissions.BasePermission):

    message = "Benutzer hat keine Berechtigung, diese Bestellung zu aktualisieren."

    def has_object_permission(self, request, view, obj):

        return obj.customer_user == request.user or obj.business_user == request.user
