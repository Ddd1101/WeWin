from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Enterprise


@admin.register(Enterprise)
class EnterpriseAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact_person', 'contact_phone', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'code', 'contact_person']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username', 'email', 'first_name', 'last_name',
        'user_type', 'enterprise', 'is_active', 'is_staff', 'created_at'
    ]
    list_filter = ['user_type', 'is_active', 'is_staff', 'enterprise', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'enterprise', 'phone', 'avatar', 'created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'enterprise', 'phone', 'avatar')
        }),
    )
