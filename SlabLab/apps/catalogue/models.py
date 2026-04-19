from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    """Card categories with optional parent for sub-categories."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='children'
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        if self.parent:
            return f'{self.parent.name} → {self.name}'
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def is_subcategory(self):
        return self.parent is not None

    def get_all_cards(self):
        """Get cards from this category and all subcategories."""
        categories = Category.objects.filter(
            models.Q(pk=self.pk) | models.Q(parent=self)
        )
        return Card.objects.filter(category__in=categories, is_active=True)


class Card(models.Model):
    """The main product — a graded collectible card."""

    CONDITION_CHOICES = [
        ('mint', 'Mint'),
        ('near_mint', 'Near Mint'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('ultra_rare', 'Ultra Rare'),
        ('secret_rare', 'Secret Rare'),
        ('promo', 'Promo'),
    ]
    GRADING_COMPANY_CHOICES = [
        ('psa', 'PSA'),
        ('bgs', 'BGS (Beckett)'),
        ('cgc', 'CGC'),
        ('sgc', 'SGC'),
        ('raw', 'Raw (Ungraded)'),
    ]
    PRICING_CHOICES = [
        ('fixed', 'Fixed Price'),
        ('auction', 'Auction'),
        ('offer', 'Open to Offers'),
    ]

    # Basic info
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, related_name='cards'
    )

    # Card-specific metadata
    set_name = models.CharField(max_length=150, blank=True, help_text='e.g. Base Set, Topps Chrome')
    edition = models.CharField(max_length=100, blank=True, help_text='e.g. 1st Edition, Unlimited')
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, default='common')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='near_mint')
    language = models.CharField(max_length=50, default='English')
    print_run = models.PositiveIntegerField(null=True, blank=True, help_text='Total copies printed')
    year = models.PositiveIntegerField(null=True, blank=True)
    brand = models.CharField(max_length=100, blank=True, help_text='e.g. Pokémon, Topps, Panini')

    # Grading
    grading_company = models.CharField(max_length=10, choices=GRADING_COMPANY_CHOICES, default='raw')
    grade = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text='Numeric grade, e.g. 9.5'
    )
    serial_number = models.CharField(max_length=100, blank=True)
    population = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Number of copies at this grade'
    )

    # Pricing & inventory
    price = models.DecimalField(max_digits=10, decimal_places=2)
    pricing_type = models.CharField(max_length=10, choices=PRICING_CHOICES, default='fixed')
    stock = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    # Images
    image = models.ImageField(upload_to='cards/', blank=True, null=True)
    image_back = models.ImageField(upload_to='cards/', blank=True, null=True)

    # Ownership
    seller = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='listed_cards', null=True, blank=True
    )

    # Stats
    views_count = models.PositiveIntegerField(default=0)
    featured = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Card.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_in_stock(self):
        return self.stock > 0

    @property
    def grade_display(self):
        if self.grading_company == 'raw':
            return 'Raw'
        return f'{self.get_grading_company_display()} {self.grade}'

    def average_rating(self):
        from apps.interactions.models import Review
        reviews = Review.objects.filter(card=self)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    def review_count(self):
        from apps.interactions.models import Review
        return Review.objects.filter(card=self).count()
