#!/usr/bin/env python3
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wewin.settings')
django.setup()

from account.models import User, UserType

print("=" * 60)
print("将 admin 用户设置为超级管理员")
print("=" * 60)

# 查找admin用户
try:
    user = User.objects.get(username='admin')
    print(f"\n找到用户: {user.username}")
    print(f"当前用户类型: {user.get_user_type_display()}")
    print(f"当前 is_superuser: {user.is_superuser}")
    print(f"当前 is_staff: {user.is_staff}")
    
    # 更新为超级管理员
    user.user_type = UserType.SUPER_ADMIN
    user.is_superuser = True
    user.is_staff = True
    user.save()
    
    print("\n✓ 更新成功！")
    print(f"新用户类型: {user.get_user_type_display()}")
    print(f"新 is_superuser: {user.is_superuser}")
    print(f"新 is_staff: {user.is_staff}")
    
except User.DoesNotExist:
    print("\n✗ 错误: 找不到用户名为 'admin' 的用户")
    print("请先创建该用户或使用其他用户名")
except Exception as e:
    print(f"\n✗ 发生错误: {e}")

print("\n" + "=" * 60)
