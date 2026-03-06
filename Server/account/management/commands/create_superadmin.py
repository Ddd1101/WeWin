from django.core.management.base import BaseCommand
from account.models import User, UserType


class Command(BaseCommand):
    help = '创建默认的网站超级管理员账户'

    def handle(self, *args, **options):
        username = 'superadmin'
        password = 'superadmin123'
        email = 'superadmin@example.com'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'用户 "{username}" 已存在'))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            user_type=UserType.SUPER_ADMIN
        )

        self.stdout.write(self.style.SUCCESS(f'成功创建网站超级管理员账户！'))
        self.stdout.write(f'用户名: {username}')
        self.stdout.write(f'密码: {password}')
        self.stdout.write(f'邮箱: {email}')
