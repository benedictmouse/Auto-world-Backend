from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """
    Permission check for admin users (staff/superuser)
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsApprovedWorkerOrAdmin(permissions.BasePermission):
    """
    Permission check for approved workers and admins
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Admins always have access
        if request.user.is_staff:
            return True
        
        # Workers must be approved
        return request.user.is_approved


class IsApprovedWorker(permissions.BasePermission):
    """
    Permission check for approved workers only (not admins)
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_approved and 
            not request.user.is_staff
        )