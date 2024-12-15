from rest_framework import permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'

class IsEditor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'editor'

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'

class IsAdminOrEditorReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        if request.method in permissions.SAFE_METHODS:
            return request.user.role in ['admin', 'editor']
            
        if request.method in ['POST', 'PUT', 'PATCH']:
            return request.user.role in ['admin', 'editor']
            
        return request.user.role == 'admin'  # For DELETE
