from django.core.management.base import BaseCommand
from account.models import PageConfig, UserType


class Command(BaseCommand):
    help = '初始化页面配置数据'

    def handle(self, *args, **options):
        pages = [
            {'name': '数据概览', 'route': 'dashboard', 'order': 1},
            {'name': '店铺管理', 'route': 'stores', 'order': 2},
            {'name': '商品管理', 'route': 'products', 'order': 3},
            {'name': '库存管理', 'route': 'inventory', 'order': 4},
            {'name': '销售数据', 'route': 'sales', 'order': 5},
            {'name': '用户管理', 'route': 'users', 'order': 6},
        ]

        user_types = [
            UserType.SUPER_ADMIN,
            UserType.SITE_ADMIN,
            UserType.ENTERPRISE_ADMIN,
            UserType.ENTERPRISE_USER,
            UserType.TEMPORARY,
        ]

        for user_type in user_types:
            for page in pages:
                is_visible = True
                if user_type == UserType.ENTERPRISE_ADMIN:
                    is_visible = page['route'] != 'users'
                elif user_type == UserType.ENTERPRISE_USER:
                    is_visible = page['route'] in ['dashboard', 'products', 'inventory']
                elif user_type == UserType.TEMPORARY:
                    is_visible = page['route'] == 'dashboard'

                PageConfig.objects.get_or_create(
                    user_type=user_type,
                    page_route=page['route'],
                    defaults={
                        'page_name': page['name'],
                        'is_visible': is_visible,
                        'order': page['order']
                    }
                )

        self.stdout.write(self.style.SUCCESS('成功初始化页面配置数据！'))
