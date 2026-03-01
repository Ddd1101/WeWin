from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'category', 'company', 'is_active', 'created_at']
    list_filter = ['platform', 'category', 'is_active', 'created_at', 'company']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['managers']
