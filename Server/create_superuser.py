import os
import django
from django.contrib.auth.hashers import make_password

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wewin.settings')
django.setup()

from account.models import User
from company.models import Company

print("Creating superuser...")

# 创建默认公司
company, created = Company.objects.get_or_create(
    name="默认企业",
    code="DEFAULT"
)
print(f"Company created: {created}")

# 创建超级管理员用户
user, created = User.objects.get_or_create(
    username="admin",
    defaults={
        'password': make_password('admin123'),
        'is_superuser': True,
        'is_staff': True,
        'is_active': True,
        'user_type': 'super_admin',
        'company': company,
        'real_name': '超级管理员'
    }
)

if created:
    print("Superuser created successfully")
else:
    print("Superuser already exists")

print(f"Username: admin")
print(f"Password: admin123")
