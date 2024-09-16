from rest_framework.permissions import BasePermission

class IsBookOwner(BasePermission):
    """
    Custom permission to only allow owners of a book or superusers to access it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user == obj.user or request.user.is_superuser
