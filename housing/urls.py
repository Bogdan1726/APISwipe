from django.urls import include, path
from rest_framework.routers import DefaultRouter
from housing.views import (
    ResidentialComplexViewSet, ResidentialComplexNewsViewSet, ResidentialComplexDocumentViewSet,
    FavoritesResidentialComplexViewSet
)

app_name = 'housing'

router = DefaultRouter()
router.register('complex', ResidentialComplexViewSet, basename='residential-complex'),
router.register('complex-news', ResidentialComplexNewsViewSet, basename='residential-complex-news')
router.register('complex-document', ResidentialComplexDocumentViewSet, basename='residential-complex-document')
router.register('complex-favorites', FavoritesResidentialComplexViewSet, basename='residential-complex-favorites')

urlpatterns = [
    path('', include(router.urls))
]
