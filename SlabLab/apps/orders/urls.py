from django.urls import path
from . import views

urlpatterns = [
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:card_id>/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_item_view, name='update_cart_item'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),

    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),

    # Order history
    path('orders/', views.order_history_view, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),

    # Admin — Order management
    path('manage/orders/', views.admin_order_list_view, name='admin_order_list'),
    path('manage/orders/<int:order_id>/', views.admin_order_detail_view, name='admin_order_detail'),
]
