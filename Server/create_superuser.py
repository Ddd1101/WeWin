#!/usr/bin/env python
"""创建超级管理员账户的脚本"""
import os
import sys

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wewin.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from account.models import User

# 创建超级管理员
def create_superuser():
    username = 'admin'
    email = 'admin@wewin.com'
    password = 'admin123'
    
    # 检查用户是否已存在
    if User.objects.filter(username=username).exists():
        print(f'用户 {username} 已存在')
        # 更新为超级管理员
        user = User.objects.get(username=username)
        user.user_type = 'super_admin'
        user.is_superuser = True
        user.is_staff = True
        user.save()
        print(f'已更新用户 {username} 为超级管理员')
    else:
        # 创建新用户
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            user_type='super_admin'
        )
        print(f'超级管理员创建成功！')
        print(f'用户名: {username}')
        print(f'密码: {password}')
        print(f'邮箱: {email}')
        print(f'用户类型: 网站超级管理员')

if __name__ == '__main__':
    create_superuser()
