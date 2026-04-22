from django.urls import path
from . import views

urlpatterns = [
    # Public browsing
    path('', views.card_list_view, name='card_list'),
    path('card/<slug:slug>/', views.card_detail_view, name='card_detail'),
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail_view, name='category_detail'),


]
