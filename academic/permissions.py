# permissions.py
from rest_framework import permissions

class IsHeadUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow any authenticated user for GET requests (retrieve)
        if request.method == 'GET':
            return request.user.is_authenticated
        # Check if the user is authenticated and has the user_type "Head" for other methods
        return request.user.is_authenticated and request.user.user_type == 'H'
    
    
    
class IsHeadAndTeacherUser(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow any authenticated user for GET requests (retrieve)
        if request.method == 'GET':
            return request.user.is_authenticated
        # Check if the user is authenticated and has the user_type "Head" or "Teacher" for other methods
        return request.user.is_authenticated and request.user.user_type in ['H', 'T']

