from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg
from django.http import JsonResponse

from .models import Card, Category
from .forms import CardForm, CategoryForm, AdvancedSearchForm
from apps.interactions.models import RecentlyViewed


# ── Home ─────────────────────────────────────────────────────────────────────
def home_view(request):
    """Landing page with featured cards, categories, and latest listings."""
    featured_cards = Card.objects.filter(
        is_active=True, featured=True
    ).select_related('category', 'seller')[:8]

    latest_cards = Card.objects.filter(
        is_active=True
    ).select_related('category', 'seller')[:12]

    categories = Category.objects.filter(
        is_active=True, parent__isnull=True
    ).prefetch_related('children')

    context = {
        'featured_cards': featured_cards,
        'latest_cards': latest_cards,
        'categories': categories,
    }
    return render(request, 'home.html', context)


# ── Card Listing ─────────────────────────────────────────────────────────────
def card_list_view(request):
    """Browse all cards with search and advanced filtering."""
    form = AdvancedSearchForm(request.GET or None)
    cards = Card.objects.filter(is_active=True).select_related('category', 'seller')

    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        rarity = form.cleaned_data.get('rarity')
        condition = form.cleaned_data.get('condition')
        grading = form.cleaned_data.get('grading_company')
        brand = form.cleaned_data.get('brand')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        year = form.cleaned_data.get('year')
        sort = form.cleaned_data.get('sort') or '-created_at'

        # Text search — searches name AND set_name (the second important characteristic)
        if q:
            cards = cards.filter(
                Q(title__icontains=q) |
                Q(set_name__icontains=q) |
                Q(brand__icontains=q) |
                Q(description__icontains=q)
            )
        if category:
            # Include subcategories
            cards = cards.filter(
                Q(category=category) | Q(category__parent=category)
            )
        if rarity:
            cards = cards.filter(rarity=rarity)
        if condition:
            cards = cards.filter(condition=condition)
        if grading:
            cards = cards.filter(grading_company=grading)
        if brand:
            cards = cards.filter(brand__icontains=brand)
        if min_price is not None:
            cards = cards.filter(price__gte=min_price)
        if max_price is not None:
            cards = cards.filter(price__lte=max_price)
        if year:
            cards = cards.filter(year=year)

        cards = cards.order_by(sort)
    else:
        cards = cards.order_by('-created_at')

    paginator = Paginator(cards, 24)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'form': form,
        'page_obj': page,
        'total_results': paginator.count,
    }
    return render(request, 'catalogue/list.html', context)


# ── Card Detail ──────────────────────────────────────────────────────────────
def card_detail_view(request, slug):
    """Single card detail page with reviews and recommendations."""
    card = get_object_or_404(Card, slug=slug, is_active=True)

    # Increment view count
    Card.objects.filter(pk=card.pk).update(views_count=card.views_count + 1)

    # Track recently viewed for logged-in users
    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(
            user=request.user, card=card,
            defaults={}
        )

    # Reviews
    from apps.interactions.models import Review, Wishlist
    reviews = Review.objects.filter(card=card).select_related('user').order_by('-created_at')

    # Check if user already reviewed / wishlisted
    user_has_reviewed = False
    user_has_wishlisted = False
    if request.user.is_authenticated:
        user_has_reviewed = Review.objects.filter(card=card, user=request.user).exists()
        user_has_wishlisted = Wishlist.objects.filter(card=card, user=request.user).exists()

    # Recommendations — cards from same category/set/brand
    recommended = Card.objects.filter(
        is_active=True
    ).exclude(pk=card.pk).filter(
        Q(category=card.category) |
        Q(set_name=card.set_name) |
        Q(brand=card.brand)
    ).distinct().order_by('-views_count')[:6]

    context = {
        'card': card,
        'reviews': reviews,
        'user_has_reviewed': user_has_reviewed,
        'user_has_wishlisted': user_has_wishlisted,
        'recommended': recommended,
        'avg_rating': card.average_rating(),
        'review_count': card.review_count(),
    }
    return render(request, 'catalogue/detail.html', context)


# ── Category Browse ──────────────────────────────────────────────────────────
def category_list_view(request):
    """Browse all top-level categories."""
    categories = Category.objects.filter(
        is_active=True, parent__isnull=True
    ).prefetch_related('children')
    return render(request, 'catalogue/category.html', {'categories': categories})


def category_detail_view(request, slug):
    """Browse cards within a category."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    subcategories = category.children.filter(is_active=True)

    cards = category.get_all_cards().select_related('seller')

    # Simple sort
    sort = request.GET.get('sort', '-created_at')
    valid_sorts = ['price', '-price', 'title', '-created_at', '-views_count']
    if sort in valid_sorts:
        cards = cards.order_by(sort)

    paginator = Paginator(cards, 24)
    page = paginator.get_page(request.GET.get('page', 1))

    context = {
        'category': category,
        'subcategories': subcategories,
        'page_obj': page,
    }
    return render(request, 'catalogue/category_detail.html', context)


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — Catalogue Management
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


# ── Admin Dashboard ──────────────────────────────────────────────────────────
@admin_required
def admin_dashboard_view(request):
    """Admin overview page."""
    from django.contrib.auth.models import User
    from apps.orders.models import Order

    context = {
        'total_cards': Card.objects.count(),
        'active_cards': Card.objects.filter(is_active=True).count(),
        'total_categories': Category.objects.count(),
        'total_users': User.objects.count(),
        'total_orders': Order.objects.count(),
        'recent_cards': Card.objects.order_by('-created_at')[:5],
        'recent_orders': Order.objects.order_by('-created_at')[:5],
    }
    return render(request, 'admin_panel/dashboard.html', context)


# ── Card CRUD ────────────────────────────────────────────────────────────────
@admin_required
def admin_card_list_view(request):
    """List all cards for admin management."""
    cards = Card.objects.select_related('category', 'seller').order_by('-created_at')
    query = request.GET.get('q', '')
    if query:
        cards = cards.filter(
            Q(title__icontains=query) | Q(set_name__icontains=query)
        )
    paginator = Paginator(cards, 25)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'admin_panel/manage_catalogue.html', {
        'page_obj': page, 'query': query,
    })


@admin_required
def admin_card_create_view(request):
    """Admin creates a new card."""
    if request.method == 'POST':
        form = CardForm(request.POST, request.FILES)
        if form.is_valid():
            card = form.save(commit=False)
            card.seller = request.user
            card.save()
            messages.success(request, f'Card "{card.title}" created.')
            return redirect('admin_card_list')
    else:
        form = CardForm()
    return render(request, 'admin_panel/card_form.html', {
        'form': form, 'action': 'Create',
    })


@admin_required
def admin_card_edit_view(request, card_id):
    """Admin edits an existing card."""
    card = get_object_or_404(Card, pk=card_id)
    if request.method == 'POST':
        form = CardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, f'Card "{card.title}" updated.')
            return redirect('admin_card_list')
    else:
        form = CardForm(instance=card)
    return render(request, 'admin_panel/card_form.html', {
        'form': form, 'card': card, 'action': 'Edit',
    })


@admin_required
def admin_card_delete_view(request, card_id):
    """Admin deletes a card."""
    card = get_object_or_404(Card, pk=card_id)
    if request.method == 'POST':
        title = card.title
        card.delete()
        messages.success(request, f'Card "{title}" deleted.')
        return redirect('admin_card_list')
    return render(request, 'admin_panel/confirm_delete_card.html', {'card': card})


# ── Category CRUD ────────────────────────────────────────────────────────────
@admin_required
def admin_category_list_view(request):
    """List all categories for admin."""
    categories = Category.objects.select_related('parent').order_by('name')
    return render(request, 'admin_panel/manage_categories.html', {
        'categories': categories,
    })


@admin_required
def admin_category_create_view(request):
    """Admin creates a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created.')
            return redirect('admin_category_list')
    else:
        form = CategoryForm()
    return render(request, 'admin_panel/category_form.html', {
        'form': form, 'action': 'Create',
    })


@admin_required
def admin_category_edit_view(request, category_id):
    """Admin edits an existing category."""
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, f'Category "{category.name}" updated.')
            return redirect('admin_category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'admin_panel/category_form.html', {
        'form': form, 'category': category, 'action': 'Edit',
    })


@admin_required
def admin_category_delete_view(request, category_id):
    """Admin deletes a category."""
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        name = category.name
        category.delete()
        messages.success(request, f'Category "{name}" deleted.')
        return redirect('admin_category_list')
    return render(request, 'admin_panel/confirm_delete_category.html', {
        'category': category,
    })
