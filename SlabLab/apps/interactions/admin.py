from django.contrib import admin
from .models import Review, Wishlist, RecentlyViewed, SearchHistory


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'card', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'card__title', 'comment')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'card', 'added_at')
    search_fields = ('user__username', 'card__title')


@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ('user', 'card', 'viewed_at')
    search_fields = ('user__username', 'card__title')


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'brand', 'rarity', 'searched_at')
    search_fields = ('user__username', 'query')
    list_filter = ('rarity', 'searched_at')
