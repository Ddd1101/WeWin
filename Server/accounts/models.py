from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class UserType(models.TextChoices):
    SUPER_ADMIN = 'super_admin', '网站超级管理员'
    SITE_ADMIN = 'site_admin', '网站管理员'
    ENTERPRISE_ADMIN = 'enterprise_admin', '企业用户管理员'
    ENTERPRISE_USER = 'enterprise_user', '企业用户普通账户'
    TEMPORARY = 'temporary', '临时账户'


class Enterprise(models.Model):
    name = models.CharField(max_length=200, verbose_name='企业名称', unique=True)
    code = models.CharField(max_length=50, verbose_name='企业编号', unique=True)
    address = models.CharField(max_length=500, verbose_name='企业地址', blank=True, null=True)
    contact_person = models.CharField(max_length=100, verbose_name='联系人', blank=True, null=True)
    contact_phone = models.CharField(max_length=50, verbose_name='联系电话', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '企业信息'
        verbose_name_plural = '企业信息'

    def __str__(self):
        return f'{self.name} ({self.code})'


class User(AbstractUser):
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.TEMPORARY,
        verbose_name='用户类型'
    )
    enterprise = models.ForeignKey(
        Enterprise,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='所属企业',
        related_name='users'
    )
    phone = models.CharField(max_length=50, verbose_name='手机号', blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', verbose_name='头像', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return f'{self.username} - {self.get_user_type_display()}'

    @property
    def is_super_admin(self):
        return self.user_type == UserType.SUPER_ADMIN

    @property
    def is_site_admin(self):
        return self.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]

    @property
    def is_enterprise_admin(self):
        return self.user_type == UserType.ENTERPRISE_ADMIN

    @property
    def can_manage_users(self):
        return self.is_site_admin or self.is_enterprise_admin
