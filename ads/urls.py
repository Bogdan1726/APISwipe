from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ads.views import (
    AnnouncementViewSet, AnnouncementComplaintViewSet,
    AnnouncementAdvertisingViewSet, FavoritesAnnouncementViewSet,
    ApartmentViewSet, AnnouncementModerationViewSet
)

app_name = 'ads'

router = DefaultRouter()
router.register('apartment', ApartmentViewSet, basename='apartment')
router.register('announcement', AnnouncementViewSet, basename='announcement'),
router.register('announcement-complaint', AnnouncementComplaintViewSet, basename='announcement-complaint')
router.register('announcement-advertising', AnnouncementAdvertisingViewSet, basename='announcement-advertising')
router.register('announcement-favorites', FavoritesAnnouncementViewSet, basename='announcement-favorites')
router.register('announcement-moderation', AnnouncementModerationViewSet, basename='announcement-moderation')

urlpatterns = [
    path('', include(router.urls))
]
