from rest_framework import permissions


class IsMyFilter(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return bool(request.user.user_filter.filter(id=obj.pk).exists())


class IsMyResidentialComplex(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_developer:
            return request.user.user_residential_complex.id is obj.pk
        return False


class IsMyResidentialComplexObject(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_developer:
            return request.user.user_residential_complex.id is obj.residential_complex.pk
        return False


class IsMyApartment(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.user_apartment.filter(id=obj.pk).exists()
