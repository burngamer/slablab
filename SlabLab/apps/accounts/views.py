from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from .forms import RegistrationForm, LoginForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile
from apps.orders.models import Order
from apps.interactions.models import Review, Wishlist, RecentlyViewed


# ── Registration ─────────────────────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set role on profile
            user.profile.role = form.cleaned_data['role']
            user.profile.save()
            login(request, user)
            messages.success(request, f'Welcome to Slab Lab, {user.first_name}!')
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


# ── Login / Logout ───────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ── Profile ──────────────────────────────────────────────────────────────────
@login_required
def profile_view(request):
    """View current user's profile."""
    profile = request.user.profile
    return render(request, 'accounts/profile.html', {'profile': profile})


@login_required
def profile_edit_view(request):
    """Edit current user's profile."""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


# ── Dashboard ────────────────────────────────────────────────────────────────
@login_required
def dashboard_view(request):
    """Personalized dashboard showing recent activity."""
    user = request.user

    # Recent orders
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]

    # Recently viewed cards
    recently_viewed = RecentlyViewed.objects.filter(
        user=user
    ).select_related('card').order_by('-viewed_at')[:8]

    # User's reviews
    user_reviews = Review.objects.filter(user=user).order_by('-created_at')[:5]

    # Wishlist count
    wishlist_items = Wishlist.objects.filter(user=user).select_related('card')[:8]

    context = {
        'recent_orders': recent_orders,
        'recently_viewed': recently_viewed,
        'user_reviews': user_reviews,
        'wishlist_items': wishlist_items,
    }
    return render(request, 'accounts/dashboard.html', context)


# ── Public user profile ─────────────────────────────────────────────────────
def public_profile_view(request, username):
    """View any user's public profile."""
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    if not profile.is_public and request.user != profile_user:
        messages.warning(request, 'This profile is private.')
        return redirect('home')
    reviews = Review.objects.filter(user=profile_user).order_by('-created_at')[:10]
    return render(request, 'accounts/public_profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'reviews': reviews,
    })


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN — User Management (custom, not Django admin)
# ══════════════════════════════════════════════════════════════════════════════
def admin_required(view_func):
    """Decorator: only allow users with admin role."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'profile') or not request.user.profile.is_admin:
            messages.error(request, 'Access denied. Administrators only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@admin_required
def admin_user_list_view(request):
    """List all users for admin management."""
    users = User.objects.select_related('profile').order_by('-date_joined')
    query = request.GET.get('q', '')
    if query:
        users = users.filter(username__icontains=query) | users.filter(email__icontains=query)
    paginator = Paginator(users, 20)
    page = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'admin_panel/manage_users.html', {
        'page_obj': page, 'query': query,
    })


@admin_required
def admin_user_edit_view(request, user_id):
    """Admin can edit any user's profile & role."""
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=target_user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=target_user.profile
        )
        role = request.POST.get('role', 'buyer')
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            prof = profile_form.save(commit=False)
            prof.role = role
            prof.save()
            messages.success(request, f'User {target_user.username} updated.')
            return redirect('admin_user_list')
    else:
        user_form = UserUpdateForm(instance=target_user)
        profile_form = ProfileUpdateForm(instance=target_user.profile)
    return render(request, 'admin_panel/edit_user.html', {
        'target_user': target_user,
        'user_form': user_form,
        'profile_form': profile_form,
    })


@admin_required
def admin_user_delete_view(request, user_id):
    """Admin can delete a user."""
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        messages.success(request, f'User {username} deleted.')
        return redirect('admin_user_list')
    return render(request, 'admin_panel/confirm_delete_user.html', {
        'target_user': target_user,
    })
