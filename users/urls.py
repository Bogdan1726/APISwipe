from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import (
    NotaryViewSet, UserProfileViewSet,
    UserAgentViewSet, UserSubscriptionViewSet,
    MessageViewSet, FilterViewSet, UserListViewSet
)

app_name = 'users'

router = DefaultRouter()
router.register('user-profile', UserProfileViewSet, basename='user-profile')
router.register('user-agent', UserAgentViewSet, basename='user-agent')
router.register('user-subscription', UserSubscriptionViewSet, basename='user-subscription')
router.register('user-message', MessageViewSet, basename='user-message')
router.register('user-filter', FilterViewSet, basename='user-filter')
router.register('user-list', UserListViewSet, basename='user-list')
router.register('notary', NotaryViewSet, basename='notary')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='rest_login'),
    path('registration/', RegisterView.as_view(), name='rest_register'),
]
