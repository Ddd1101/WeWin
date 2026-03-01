from account.models import User, UserType

# 检查是否存在超级管理员账户
superadmin = User.objects.filter(username='superadmin').first()

if superadmin:
    print(f'超级管理员账户已存在，用户名: {superadmin.username}')
    # 修改密码
    superadmin.set_password('superadmin123')
    superadmin.save()
    print('密码已重置为: superadmin123')
else:
    # 创建新的超级管理员账户
    superadmin = User.objects.create_superuser(
        username='superadmin',
        email='superadmin@example.com',
        password='superadmin123',
        user_type=UserType.SUPER_ADMIN
    )
    print('成功创建超级管理员账户！')
    print(f'用户名: {superadmin.username}')
    print(f'密码: superadmin123')
    print(f'邮箱: {superadmin.email}')

print('操作完成！')