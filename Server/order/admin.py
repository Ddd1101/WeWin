from django.contrib import admin
from .models import Buyer, Order, OrderItem, OrderLogistics, OrderStep


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class OrderLogisticsInline(admin.TabularInline):
    model = OrderLogistics
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


class OrderStepInline(admin.TabularInline):
    model = OrderStep
    extra = 0
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform_login_id', 'store', 'total_orders', 'total_amount', 'created_at']
    list_filter = ['store', 'created_at']
    search_fields = ['name', 'platform_login_id', 'platform_user_id', 'phone']
    readonly_fields = ['uid', 'created_at', 'updated_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['platform_order_id', 'store', 'buyer', 'status', 'total_amount', 'platform_create_time', 'created_at']
    list_filter = ['store', 'status', 'platform_create_time', 'created_at']
    search_fields = ['platform_order_id', 'platform_order_id_str']
    readonly_fields = ['uid', 'created_at', 'updated_at']
    inlines = [OrderItemInline, OrderLogisticsInline, OrderStepInline]
    date_hierarchy = 'platform_create_time'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'price', 'quantity', 'item_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['product_name', 'product_cargo_number', 'platform_sub_order_id']
    readonly_fields = ['uid', 'created_at', 'updated_at']


@admin.register(OrderLogistics)
class OrderLogisticsAdmin(admin.ModelAdmin):
    list_display = ['order', 'logistics_bill_no', 'status', 'delivered_time', 'created_at']
    list_filter = ['status', 'delivered_time', 'created_at']
    search_fields = ['logistics_bill_no', 'logistics_code']
    readonly_fields = ['uid', 'created_at', 'updated_at']


@admin.register(OrderStep)
class OrderStepAdmin(admin.ModelAdmin):
    list_display = ['order', 'step_no', 'step_name', 'pay_status', 'logistics_status', 'created_at']
    list_filter = ['pay_status', 'logistics_status', 'created_at']
    search_fields = ['step_name']
    readonly_fields = ['uid', 'created_at', 'updated_at']
