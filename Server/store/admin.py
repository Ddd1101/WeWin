from django.contrib import admin
from .models import (
    Store, PlatformApiConfig, Order, OrderItem, OrderReceiver,
    DataPullTask, StoreDataConfig, StoreData
)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'category', 'company', 'is_active', 'created_at']
    list_filter = ['platform', 'category', 'is_active', 'created_at', 'company']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['managers']


@admin.register(PlatformApiConfig)
class PlatformApiConfigAdmin(admin.ModelAdmin):
    list_display = ['store', 'app_key', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['store__name', 'app_key']
    readonly_fields = ['created_at', 'updated_at']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class OrderReceiverInline(admin.StackedInline):
    model = OrderReceiver
    extra = 0
    max_num = 1
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['platform_order_id', 'store', 'order_status', 'total_amount', 'create_time', 'synced_at']
    list_filter = ['store', 'order_status', 'refund_status', 'create_time', 'synced_at']
    search_fields = ['platform_order_id', 'platform_order_no', 'buyer_login_id']
    readonly_fields = ['synced_at', 'updated_at']
    inlines = [OrderItemInline, OrderReceiverInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'price', 'item_amount', 'created_at']
    list_filter = ['item_status', 'item_refund_status', 'created_at']
    search_fields = ['product_name', 'product_cargo_number', 'platform_item_id']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(OrderReceiver)
class OrderReceiverAdmin(admin.ModelAdmin):
    list_display = ['order', 'receiver_name', 'receiver_mobile', 'province', 'city', 'created_at']
    list_filter = ['province', 'city', 'created_at']
    search_fields = ['receiver_name', 'receiver_mobile', 'full_address']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(DataPullTask)
class DataPullTaskAdmin(admin.ModelAdmin):
    list_display = ['store', 'task_type', 'status', 'order_count', 'created_at']
    list_filter = ['store', 'task_type', 'status', 'created_at']
    search_fields = ['store__name', 'task_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StoreDataConfig)
class StoreDataConfigAdmin(admin.ModelAdmin):
    list_display = ['store', 'auto_pull_enabled', 'pull_interval_hours', 'last_pull_time', 'next_pull_time', 'created_at']
    list_filter = ['auto_pull_enabled', 'pull_status', 'created_at']
    search_fields = ['store__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(StoreData)
class StoreDataAdmin(admin.ModelAdmin):
    list_display = ['store', 'data_type', 'data_date', 'created_at']
    list_filter = ['store', 'data_type', 'data_date', 'created_at']
    search_fields = ['store__name', 'data_type']
    readonly_fields = ['created_at', 'updated_at']
