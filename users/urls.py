from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter
from users.views import (
    NotaryViewSet, UserProfileViewSet,
    UserAgentViewSet, UserSubscriptionViewSet,
    MessageViewSet, FilterViewSet
)

app_name = 'users'

router = DefaultRouter()
router.register('profile', UserProfileViewSet, basename='profile')
router.register('agent', UserAgentViewSet, basename='agent')
router.register('subscription', UserSubscriptionViewSet, basename='subscription')
router.register('message', MessageViewSet, basename='message')
router.register('filter', FilterViewSet, basename='filter')
router.register('notary', NotaryViewSet)


# print(router.urls)

urlpatterns = [
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('registration/', RegisterView.as_view(), name='rest_register'),

    # path('message/?<str:pk>/', MessageViewSet.as_view({'get': 'list'})),
    # path('message/', MessageViewSet.as_view({'post': 'create'}))
]

urlpatterns += router.urls
