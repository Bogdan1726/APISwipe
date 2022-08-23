from django.urls import include, path
from rest_framework.routers import DefaultRouter
from housing.views import (
    ResidentialComplexViewSet, ResidentialComplexNewsViewSet, ResidentialComplexDocumentViewSet,
    ApartmentViewSet
)

app_name = 'housing'

router = DefaultRouter()
router.register('complex', ResidentialComplexViewSet, basename='complex'),
router.register('complex-news', ResidentialComplexNewsViewSet, basename='complex-news')
router.register('complex-document', ResidentialComplexDocumentViewSet, basename='complex-document')
router.register('apartment', ApartmentViewSet)


urlpatterns = [
]

urlpatterns += router.urls
