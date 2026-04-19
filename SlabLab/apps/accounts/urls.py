from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('user/<str:username>/', views.public_profile_view, name='public_profile'),

    # Admin — User management
    path('manage/users/', views.admin_user_list_view, name='admin_user_list'),
    path('manage/users/<int:user_id>/edit/', views.admin_user_edit_view, name='admin_user_edit'),
    path('manage/users/<int:user_id>/delete/', views.admin_user_delete_view, name='admin_user_delete'),
]
