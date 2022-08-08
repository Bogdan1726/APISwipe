from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView
from django.urls import path
from rest_framework.routers import SimpleRouter, DefaultRouter

from users.views import NotaryViewSet, ProfileViewSet

app_name = 'users'

router = SimpleRouter()
router.register('notary', NotaryViewSet),
router.register('profile', ProfileViewSet)


urlpatterns = [
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('registration/', RegisterView.as_view(), name='rest_register'),
]

urlpatterns += router.urls
