from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from django.urls import path
from rest_framework.routers import DefaultRouter
from users.views import (
    NotaryViewSet, UserProfileViewSet,
    UserAgentViewSet, UserSubscriptionViewSet,
    MessageViewSet, FilterViewSet, UserBlackListViewSet
)

app_name = 'users'

router = DefaultRouter()
router.register('profile', UserProfileViewSet, basename='user-profile')
router.register('agent', UserAgentViewSet, basename='user-agent')
router.register('subscription', UserSubscriptionViewSet, basename='user-subscription')
router.register('message', MessageViewSet, basename='user-message')
router.register('filter', FilterViewSet, basename='user-filter')
router.register('blacklist', UserBlackListViewSet, basename='user-blacklist')
router.register('notary', NotaryViewSet, basename='notary')

urlpatterns = [
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('registration/', RegisterView.as_view(), name='rest_register'),
]

urlpatterns += router.urls
