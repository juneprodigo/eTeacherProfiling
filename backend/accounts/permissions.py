"""
accounts/permissions.py — Role-based Permission Classes
"""
from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only Admin role has access."""
    message = 'Access restricted to Administrators.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'admin')


class IsHROrAdmin(BasePermission):
    """HR Officers and Admins have access."""
    message = 'Access restricted to HR Officers and Administrators.'

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ('admin', 'hr')
        )


class IsOwnerOrHROrAdmin(BasePermission):
    """Teachers can only access their own data; HR and Admin can access all."""
    message = 'You do not have permission to access this resource.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.role in ('admin', 'hr'):
            return True
        # For Teacher objects
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # For User objects
        return obj == request.user
