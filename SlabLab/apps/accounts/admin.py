from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'city', 'country', 'created_at')
    list_filter = ('role', 'country', 'is_public')
    search_fields = ('user__username', 'user__email', 'city')
    readonly_fields = ('created_at', 'updated_at')
