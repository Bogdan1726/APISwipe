from rest_framework.routers import DefaultRouter
from ads.views import AnnouncementViewSet, AnnouncementComplaintViewSet, AnnouncementAdvertisingViewSet

app_name = 'ads'


router = DefaultRouter()
router.register('announcement', AnnouncementViewSet, basename='announcement'),
router.register('announcement-complaint', AnnouncementComplaintViewSet, basename='announcement-complaint')
router.register('announcement-advertising', AnnouncementAdvertisingViewSet, basename='announcement-advertising')


urlpatterns = [
]

urlpatterns += router.urls



