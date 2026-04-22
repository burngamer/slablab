"""
Slab Lab — Main URL configuration.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin

from apps.catalogue.views import home_view

# Custom admin views  (gathered here under /admin/)
from apps.catalogue import views as catalogue_views
from apps.accounts import views as accounts_views
from apps.orders import views as orders_views

admin_patterns = [
    # Dashboard
    path('', catalogue_views.admin_dashboard_view, name='admin_dashboard'),

    # Catalogue management
    path('cards/', catalogue_views.admin_card_list_view, name='admin_card_list'),
    path('cards/create/', catalogue_views.admin_card_create_view, name='admin_card_create'),
    path('cards/<int:card_id>/edit/', catalogue_views.admin_card_edit_view, name='admin_card_edit'),
    path('cards/<int:card_id>/delete/', catalogue_views.admin_card_delete_view, name='admin_card_delete'),
    path('categories/', catalogue_views.admin_category_list_view, name='admin_category_list'),
    path('categories/create/', catalogue_views.admin_category_create_view, name='admin_category_create'),
    path('categories/<int:category_id>/edit/', catalogue_views.admin_category_edit_view, name='admin_category_edit'),
    path('categories/<int:category_id>/delete/', catalogue_views.admin_category_delete_view, name='admin_category_delete'),

    # User management
    path('users/', accounts_views.admin_user_list_view, name='admin_user_list'),
    path('users/<int:user_id>/edit/', accounts_views.admin_user_edit_view, name='admin_user_edit'),
    path('users/<int:user_id>/delete/', accounts_views.admin_user_delete_view, name='admin_user_delete'),

    # Order management
    path('orders/', orders_views.admin_order_list_view, name='admin_order_list'),
    path('orders/<int:order_id>/', orders_views.admin_order_detail_view, name='admin_order_detail'),
]

urlpatterns = [
    # Default Django admin
    path('admin/', admin.site.urls),

    # Custom admin panel at /admin-dashboard/
    path('admin-dashboard/', include(admin_patterns)),

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
