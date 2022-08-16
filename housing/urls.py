from django.urls import include, path
from rest_framework.routers import DefaultRouter

from housing.views import ResidentialComplexViewSet

app_name = 'housing'

router = DefaultRouter()
router.register('complex', ResidentialComplexViewSet, basename='complex')


urlpatterns = [

]

urlpatterns += router.urls
