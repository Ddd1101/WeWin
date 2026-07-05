from django.contrib import admin
from .models import PurchaseList, PurchaseItem


@admin.register(PurchaseList)
class PurchaseListAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'created_by', 'assignee', 'status', 'planned_date', 'created_at']
    list_filter = ['status', 'planned_date', 'company']
    search_fields = ['title', 'notes', 'created_by__username', 'assignee__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PurchaseItem)
class PurchaseItemAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'sku_code', 'purchase_list', 'product_type', 'quantity', 'unit', 'status', 'purchased_quantity']
    list_filter = ['status', 'product_type', 'created_at']
    search_fields = ['product_name', 'sku_code', 'supplier', 'material', 'color']
    readonly_fields = ['created_at', 'updated_at']
