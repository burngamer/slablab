from django.urls import path
from . import views

urlpatterns = [
    # Public browsing
    path('', views.card_list_view, name='card_list'),
    path('card/<slug:slug>/', views.card_detail_view, name='card_detail'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail_view, name='category_detail'),

    # Admin — Catalogue management
    path('manage/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('manage/cards/', views.admin_card_list_view, name='admin_card_list'),
    path('manage/cards/create/', views.admin_card_create_view, name='admin_card_create'),
    path('manage/cards/<int:card_id>/edit/', views.admin_card_edit_view, name='admin_card_edit'),
    path('manage/cards/<int:card_id>/delete/', views.admin_card_delete_view, name='admin_card_delete'),
    path('manage/categories/', views.admin_category_list_view, name='admin_category_list'),
    path('manage/categories/create/', views.admin_category_create_view, name='admin_category_create'),
    path('manage/categories/<int:category_id>/edit/', views.admin_category_edit_view, name='admin_category_edit'),
    path('manage/categories/<int:category_id>/delete/', views.admin_category_delete_view, name='admin_category_delete'),
]
