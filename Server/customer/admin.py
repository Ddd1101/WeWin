from django.contrib import admin
from .models import Customer, CustomerVisibility, CustomerProduct, CustomerPriceHistory


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'company', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'company']
    search_fields = ['name', 'phone', 'email', 'contact_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CustomerVisibility)
class CustomerVisibilityAdmin(admin.ModelAdmin):
    list_display = ['customer', 'visible_user', 'configured_by', 'configured_at']
    list_filter = ['configured_at']
    search_fields = ['customer__name', 'visible_user__username', 'configured_by__username']
    readonly_fields = ['configured_at']


@admin.register(CustomerProduct)
class CustomerProductAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['customer__name', 'product__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CustomerPriceHistory)
class CustomerPriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'price', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['customer__name', 'product__name', 'created_by__username']
    readonly_fields = ['created_at']
