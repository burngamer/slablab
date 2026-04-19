from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator

from .models import Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm
from apps.catalogue.models import Card


# ── Cart helpers ─────────────────────────────────────────────────────────────
def _get_cart(request):
    """Get or create a cart for the current user/session."""
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


# ── Cart Views ───────────────────────────────────────────────────────────────
def cart_view(request):
    """Display the shopping cart."""
    cart = _get_cart(request)
    items = cart.items.select_related('card').all()
    return render(request, 'orders/cart.html', {
        'cart': cart,
        'items': items,
    })


@require_POST
def add_to_cart_view(request, card_id):
    """Add a card to the cart (AJAX-friendly)."""
    card = get_object_or_404(Card, pk=card_id, is_active=True)
    cart = _get_cart(request)
    quantity = int(request.POST.get('quantity', 1))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, card=card,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    # Check stock
    if cart_item.quantity > card.stock:
        cart_item.quantity = card.stock
        cart_item.save()
        msg = f'Only {card.stock} in stock. Quantity adjusted.'
    else:
        msg = f'"{card.title}" added to cart.'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': msg,
            'cart_count': cart.total_items,
        })

    messages.success(request, msg)
    return redirect('cart')


@require_POST
def update_cart_item_view(request, item_id):
    """Update quantity of a cart item."""
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        item.delete()
        msg = 'Item removed from cart.'
    else:
        if quantity > item.card.stock:
            quantity = item.card.stock
        item.quantity = quantity
        item.save()
        msg = 'Cart updated.'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': msg,
            'cart_count': cart.total_items,
            'cart_total': str(cart.total_price),
            'item_subtotal': str(item.subtotal) if quantity > 0 else '0',
        })

    messages.success(request, msg)
    return redirect('cart')


@require_POST
def remove_from_cart_view(request, item_id):
    """Remove an item from the cart."""
    cart = _get_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    title = item.card.title
    item.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': f'"{title}" removed from cart.',
            'cart_count': cart.total_items,
            'cart_total': str(cart.total_price),
        })

    messages.success(request, f'"{title}" removed from cart.')
    return redirect('cart')


# ── Checkout ─────────────────────────────────────────────────────────────────
@login_required
def checkout_view(request):
    """Checkout — review cart and enter shipping info."""
    cart = _get_cart(request)
    items = cart.items.select_related('card').all()

    if not items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('card_list')

    # Pre-fill form with profile address
    profile = request.user.profile
    initial = {
        'shipping_name': f'{request.user.first_name} {request.user.last_name}'.strip(),
        'shipping_address': profile.address_line1,
        'shipping_city': profile.city,
        'shipping_state': profile.state,
        'shipping_zip': profile.zip_code,
        'shipping_country': profile.country or 'United States',
    }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Verify stock
            for item in items:
                if item.quantity > item.card.stock:
                    messages.error(
                        request,
                        f'"{item.card.title}" only has {item.card.stock} in stock.'
                    )
                    return redirect('cart')

            # Create order
            order = Order.objects.create(
                user=request.user,
                total=cart.total_price,
                **form.cleaned_data,
            )

            # Create order items and reduce stock
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    card=item.card,
                    card_title=item.card.title,
                    quantity=item.quantity,
                    price=item.card.price,
                )
                item.card.stock -= item.quantity
                item.card.save()

            # Clear cart
            cart.items.all().delete()

            messages.success(request, f'Order #{order.pk} placed successfully!')
            return redirect('order_detail', order_id=order.pk)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart': cart,
        'items': items,
    })


# ── Order History & Detail ───────────────────────────────────────────────────
@login_required
def order_history_view(request):
    """User's past orders."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(orders, 10)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'orders/order_history.html', {'page_obj': page})


@login_required
def order_detail_view(request, order_id):
    """View a single order's details."""
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    items = order.order_items.select_related('card').all()
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items,
    })


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — Order Management
# ══════════════════════════════════════════════════════════════════════════════
def admin_required(view_func):
    """Decorator: only allow admin-role users."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, 'Access denied. Administrators only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_order_list_view(request):
    """Admin view to list all orders across the marketplace."""
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(status=status_filter)
        
    paginator = Paginator(orders, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    
    return render(request, 'admin_panel/manage_orders.html', {
        'page_obj': page,
        'status_filter': status_filter,
    })


@admin_required
def admin_order_detail_view(request, order_id):
    """Admin view to inspect an order and update its status."""
    order = get_object_or_404(Order, pk=order_id)
    items = order.order_items.select_related('card').all()
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.pk} status updated to {order.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')
        return redirect('admin_order_detail', order_id=order.pk)
        
    return render(request, 'admin_panel/admin_order_detail.html', {
        'order': order,
        'items': items,
        'status_choices': Order.STATUS_CHOICES,
    })

