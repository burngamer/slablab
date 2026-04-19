from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.catalogue.models import Card


class Review(models.Model):
    """User review / star rating for a card."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'card')  # One review per user per card
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} → {self.card.title} ({self.rating}★)'


class Wishlist(models.Model):
    """User's wishlist — simple many-to-many via this model."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'card')
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.username} ♥ {self.card.title}'


class RecentlyViewed(models.Model):
    """Track which cards a user has recently viewed."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recently_viewed')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'card')
        ordering = ['-viewed_at']

    def __str__(self):
        return f'{self.user.username} viewed {self.card.title}'


class SearchHistory(models.Model):
    """Track user search queries for the recommender system."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    category_slug = models.CharField(max_length=120, blank=True)
    rarity = models.CharField(max_length=20, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']

    def __str__(self):
        return f'{self.user.username} searched "{self.query}"'
