from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_head(user):
    return user.is_authenticated and (user.is_admin or user.user_type == 'H')


class IsHeadUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.method in SAFE_METHODS or is_head(request.user))


class IsHeadAndTeacherUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.method in SAFE_METHODS or is_head(request.user) or request.user.user_type == 'T')
