from rest_framework import permissions


class IsMyFilter(permissions.BasePermission):
    """
    Gives access to personal filters only
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user.user_filter.filter(id=obj.pk).exists())


class IsDeveloper(permissions.BasePermission):
    """
    Allows access only to developers
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_developer)

