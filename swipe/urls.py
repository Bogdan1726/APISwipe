from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
import debug_toolbar

urlpatterns = [

    path('accounts/', include('allauth.urls')),

    # api
    path('api/', include('swipe.api-urls')),

    # apps
    path('', include('users.urls', namespace='users')),
    path('ads/', include('ads.urls', namespace='ads')),
    path('housing/', include('housing.urls', namespace='housing')),

    # drf-spectacular
    path('docs/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += [path('admin/', admin.site.urls)]
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
