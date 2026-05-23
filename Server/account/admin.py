from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PageConfig


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'company', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'date_joined', 'company']
    search_fields = ['username', 'email', 'phone']
    readonly_fields = ['date_joined', 'last_login']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('额外信息', {'fields': ('user_type', 'company', 'phone', 'created_by')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('额外信息', {'fields': ('user_type', 'company', 'phone')}),
    )


@admin.register(PageConfig)
class PageConfigAdmin(admin.ModelAdmin):
    list_display = ['user_type', 'page_name', 'page_route', 'is_visible', 'order']
    list_filter = ['user_type', 'is_visible']
    search_fields = ['page_name', 'page_route']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_visible', 'order']
