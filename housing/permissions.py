from rest_framework import permissions


class IsMyFilter(permissions.BasePermission):
    """
    Gives access to personal filters only
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user.user_filter.filter(id=obj.pk).exists())


class IsMyResidentialComplex(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.user_residential_complex.filter(id=obj.pk).exists()


class IsMyResidentialComplexObject(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.user_residential_complex.filter(id=obj.residential_complex.pk).exists()


class IsMyApartment(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.user_apartment.filter(id=obj.pk).exists()
