from django.core.management.base import BaseCommand
from account.models import User, UserType


class Command(BaseCommand):
    help = '将企业用户管理员角色更新为企业负责人'

    def handle(self, *args, **options):
        # 统计需要更新的用户数量
        old_users = User.objects.filter(user_type='enterprise_admin')
        count = old_users.count()
        
        if count > 0:
            # 更新用户类型
            old_users.update(user_type=UserType.ENTERPRISE_LEADER)
            self.stdout.write(self.style.SUCCESS(f'成功将 {count} 个企业用户管理员更新为企业负责人'))
        else:
            self.stdout.write(self.style.NOTICE('没有需要更新的企业用户管理员'))
