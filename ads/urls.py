from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ads.views import (
    AnnouncementViewSet, AnnouncementComplaintViewSet,
    AnnouncementAdvertisingViewSet, FavoritesAnnouncementViewSet, ApartmentListView
)

app_name = 'ads'

router = DefaultRouter()
router.register('announcement', AnnouncementViewSet, basename='announcement'),
router.register('announcement-feed', ApartmentListView, basename='announcement-feed'),
router.register('announcement-complaint', AnnouncementComplaintViewSet, basename='announcement-complaint')
router.register('announcement-advertising', AnnouncementAdvertisingViewSet, basename='announcement-advertising')
router.register('announcement-favorites', FavoritesAnnouncementViewSet, basename='announcement-favorites')

urlpatterns = [
    path('', include(router.urls))
]
