from django.contrib import admin
from .models import Category, Card


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active', 'created_at')
    list_filter = ('is_active', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'category', 'price', 'rarity', 'condition',
        'grading_company', 'grade', 'stock', 'is_active', 'featured',
    )
    list_filter = ('is_active', 'featured', 'rarity', 'condition', 'grading_company', 'category')
    search_fields = ('title', 'set_name', 'brand', 'serial_number')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_active', 'featured', 'stock', 'price')
    readonly_fields = ('views_count', 'created_at', 'updated_at')
