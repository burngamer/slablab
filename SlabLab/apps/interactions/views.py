from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q, Count

from .models import Review, Wishlist, RecentlyViewed, SearchHistory
from .forms import ReviewForm
from apps.catalogue.models import Card, Category


# ══════════════════════════════════════════════════════════════════════════════
# REVIEWS — AJAX star ratings
# ══════════════════════════════════════════════════════════════════════════════

@login_required
@require_POST
def submit_review_view(request, card_id):
    """Submit or update a review (AJAX endpoint)."""
    card = get_object_or_404(Card, pk=card_id, is_active=True)

    # Check if user already reviewed this card
    existing = Review.objects.filter(user=request.user, card=card).first()

    if existing:
        form = ReviewForm(request.POST, instance=existing)
    else:
        form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.user = request.user
        review.card = card
        review.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Review saved!',
                'rating': review.rating,
                'comment': review.comment,
                'avg_rating': card.average_rating(),
                'review_count': card.review_count(),
                'username': request.user.username,
                'created_at': review.created_at.strftime('%b %d, %Y'),
            })

        messages.success(request, 'Review saved!')
        return redirect('card_detail', slug=card.slug)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'errors': form.errors,
        }, status=400)

    messages.error(request, 'Invalid review.')
    return redirect('card_detail', slug=card.slug)


@login_required
def delete_review_view(request, review_id):
    """Delete a user's own review."""
    review = get_object_or_404(Review, pk=review_id, user=request.user)
    card_slug = review.card.slug
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('card_detail', slug=card_slug)


# ══════════════════════════════════════════════════════════════════════════════
# WISHLIST
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def wishlist_view(request):
    """View the user's wishlist."""
    items = Wishlist.objects.filter(
        user=request.user
    ).select_related('card', 'card__category')
    return render(request, 'interactions/wishlist.html', {'items': items})


@login_required
@require_POST
def toggle_wishlist_view(request, card_id):
    """Add or remove a card from wishlist (AJAX-friendly)."""
    card = get_object_or_404(Card, pk=card_id, is_active=True)
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user, card=card
    )

    if not created:
        wishlist_item.delete()
        added = False
        msg = f'"{card.title}" removed from wishlist.'
    else:
        added = True
        msg = f'"{card.title}" added to wishlist.'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
        return JsonResponse({
            'success': True,
            'added': added,
            'message': msg,
            'wishlist_count': wishlist_count,
        })

    messages.success(request, msg)
    return redirect('card_detail', slug=card.slug)


# ══════════════════════════════════════════════════════════════════════════════
# RECOMMENDER SYSTEM
# ══════════════════════════════════════════════════════════════════════════════

def get_recommendations(request, count=8):
    """
    Content-based recommender.

    Strategy:
    1. Look at the user's recently viewed cards → recommend cards in the same
       categories, sets, and brands.
    2. Look at their search history → recommend cards matching past search
       terms, categories, and rarities.
    3. Fall back to popular (most viewed) cards.
    """
    if not request.user.is_authenticated:
        # For anonymous users, return popular cards
        return Card.objects.filter(
            is_active=True
        ).order_by('-views_count')[:count]

    user = request.user
    recommended_ids = set()

    # ── Step 1: Based on recently viewed ─────────────────────────────────
    recent_views = RecentlyViewed.objects.filter(
        user=user
    ).select_related('card').order_by('-viewed_at')[:10]

    viewed_cards = [rv.card for rv in recent_views]
    viewed_ids = {c.pk for c in viewed_cards}

    if viewed_cards:
        categories = set(c.category_id for c in viewed_cards if c.category_id)
        sets = set(c.set_name for c in viewed_cards if c.set_name)
        brands = set(c.brand for c in viewed_cards if c.brand)

        q_filter = Q()
        if categories:
            q_filter |= Q(category_id__in=categories)
        if sets:
            q_filter |= Q(set_name__in=sets)
        if brands:
            q_filter |= Q(brand__in=brands)

        similar = Card.objects.filter(
            q_filter, is_active=True
        ).exclude(pk__in=viewed_ids).order_by('-views_count')[:count]

        recommended_ids.update(c.pk for c in similar)

    # ── Step 2: Based on search history ──────────────────────────────────
    searches = SearchHistory.objects.filter(user=user).order_by('-searched_at')[:5]
    if searches:
        q_filter = Q()
        for search in searches:
            if search.query:
                q_filter |= Q(title__icontains=search.query) | Q(set_name__icontains=search.query)
            if search.brand:
                q_filter |= Q(brand__icontains=search.brand)
            if search.rarity:
                q_filter |= Q(rarity=search.rarity)
            if search.category_slug:
                q_filter |= Q(category__slug=search.category_slug)

        if q_filter:
            search_recs = Card.objects.filter(
                q_filter, is_active=True
            ).exclude(
                pk__in=viewed_ids
            ).exclude(
                pk__in=recommended_ids
            ).order_by('-views_count')[:count]
            recommended_ids.update(c.pk for c in search_recs)

    # ── Step 3: Fill with popular cards if needed ────────────────────────
    if len(recommended_ids) < count:
        remaining = count - len(recommended_ids)
        popular = Card.objects.filter(
            is_active=True
        ).exclude(
            pk__in=viewed_ids
        ).exclude(
            pk__in=recommended_ids
        ).order_by('-views_count')[:remaining]
        recommended_ids.update(c.pk for c in popular)

    return Card.objects.filter(pk__in=recommended_ids, is_active=True).order_by('-views_count')[:count]


def recommendations_view(request):
    """Page showing personalized recommendations."""
    recommendations = get_recommendations(request, count=24)
    return render(request, 'interactions/recommendations.html', {
        'recommendations': recommendations,
    })


@login_required
def track_search_view(request):
    """Record a search for the recommender (called from the search view)."""
    if request.method == 'GET':
        q = request.GET.get('q', '')
        category = request.GET.get('category', '')
        rarity = request.GET.get('rarity', '')
        brand = request.GET.get('brand', '')

        if q or category or rarity or brand:
            SearchHistory.objects.create(
                user=request.user,
                query=q,
                category_slug=category,
                rarity=rarity,
                brand=brand,
            )
            # Keep only last 50 searches
            old = SearchHistory.objects.filter(user=request.user).order_by('-searched_at')[50:]
            SearchHistory.objects.filter(pk__in=[s.pk for s in old]).delete()

    return JsonResponse({'success': True})
