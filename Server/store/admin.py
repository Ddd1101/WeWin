from django.contrib import admin
from .models import Store
from django import forms
import json


class JSONEditorWidget(forms.Textarea):
    def __init__(self, attrs=None):
        default_attrs = {'cols': 80, 'rows': 10}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'platform', 'category', 'company', 'is_active', 'created_at']
    list_filter = ['platform', 'category', 'is_active', 'created_at', 'company']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['managers']
    formfield_overrides = {
        'JSONField': {'widget': JSONEditorWidget},
    }

    fieldsets = (
        (None, {
            'fields': ('name', 'platform', 'category', 'company', 'is_active')
        }),
        ('联系信息', {
            'fields': ('shop_url', 'contact_name', 'contact_phone'),
        }),
        ('API配置', {
            'fields': ('api_config',),
            'description': '配置平台API密钥等信息，格式为JSON',
        }),
        ('其他', {
            'fields': ('description', 'managers', 'created_by'),
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
        }),
    )

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'api_config':
            kwargs['widget'] = JSONEditorWidget
        return super().formfield_for_dbfield(db_field, **kwargs)
