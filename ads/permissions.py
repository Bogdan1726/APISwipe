from rest_framework import permissions


class IsMyAnnouncement(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.user_announcement.filter(id=obj.pk).exists()


class IsMyAdvertising(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.user_announcement.filter(advertising=obj.id).exists()


class IsMyApartment(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_developer:
            return request.user.user_residential_complex.residential_complex_announcement.filter(
                announcement_apartment=obj).exists()
        return False
