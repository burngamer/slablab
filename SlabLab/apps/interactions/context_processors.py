def wishlist_count(request):
    """Make wishlist count available in all templates."""
    count = 0
    if request.user.is_authenticated:
        from .models import Wishlist
        count = Wishlist.objects.filter(user=request.user).count()
    return {'wishlist_count': count}
