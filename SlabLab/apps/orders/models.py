from django.db import models
from django.contrib.auth.models import User
from apps.catalogue.models import Card


class Cart(models.Model):
    """Shopping cart — tied to user or session for guests."""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE,
        null=True, blank=True, related_name='cart'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.user:
            return f'Cart — {self.user.username}'
        return f'Cart — session {self.session_key}'

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Individual item in a cart."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'card')

    def __str__(self):
        return f'{self.quantity}× {self.card.title}'

    @property
    def subtotal(self):
        return self.card.price * self.quantity


class Order(models.Model):
    """A completed purchase."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)

    # Shipping info (snapshot at order time)
    shipping_name = models.CharField(max_length=255)
    shipping_address = models.TextField()
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_zip = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='United States')

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.pk} — {self.user.username} — ${self.total}'

    @property
    def item_count(self):
        return sum(item.quantity for item in self.order_items.all())


class OrderItem(models.Model):
    """Line item in an order — price is frozen at purchase time."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    card = models.ForeignKey(Card, on_delete=models.SET_NULL, null=True)
    card_title = models.CharField(max_length=255)  # Snapshot in case card is deleted
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at purchase time

    def __str__(self):
        return f'{self.quantity}× {self.card_title} @ ${self.price}'

    @property
    def subtotal(self):
        return self.price * self.quantity
