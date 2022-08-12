from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter

from users.views import NotaryViewSet, UserProfileViewSet, UserAgentViewSet, UserSubscriptionViewSet, MessageViewSet

app_name = 'users'

router = DefaultRouter()
router.register('profile', UserProfileViewSet, basename='profile')
router.register('agent', UserAgentViewSet, basename='agent')
router.register('subscription', UserSubscriptionViewSet, basename='subscription')
router.register('notary', NotaryViewSet)
router.register('message', MessageViewSet, basename='message')

# print(router.urls)

urlpatterns = [
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('registration/', RegisterView.as_view(), name='rest_register'),
]

urlpatterns += router.urls
