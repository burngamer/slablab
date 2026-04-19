from django.urls import path
from . import views

urlpatterns = [
    # Reviews
    path('review/<int:card_id>/', views.submit_review_view, name='submit_review'),
    path('review/<int:review_id>/delete/', views.delete_review_view, name='delete_review'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/toggle/<int:card_id>/', views.toggle_wishlist_view, name='toggle_wishlist'),

    # Recommender
    path('recommendations/', views.recommendations_view, name='recommendations'),
    path('track-search/', views.track_search_view, name='track_search'),
]
