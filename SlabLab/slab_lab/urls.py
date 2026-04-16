"""
Slab Lab — Main URL configuration.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from apps.catalogue.views import home_view

urlpatterns = [
    # Django admin
    path('admin-panel/', admin.site.urls),

    # App routes
    path('', home_view, name='home'),
    path('accounts/', include('apps.accounts.urls')),
    path('catalogue/', include('apps.catalogue.urls')),
    path('orders/', include('apps.orders.urls')),
    path('interactions/', include('apps.interactions.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
