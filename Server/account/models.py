from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Platform(models.TextChoices):
    TAOBAO = 'taobao', '淘宝'
    TMALL = 'tmall', '天猫'
    JD = 'jd', '京东'
    PDD = 'pdd', '拼多多'
    DOUYIN = 'douyin', '抖音电商'
    KUAISHOU = 'kuaishou', '快手电商'
    ALIBABA_1688 = '1688', '1688'
    XIAOHONGSHU = 'xiaohongshu', '小红书'
    WECHAT = 'wechat', '微信小店'
    OTHER = 'other', '其他'


class Category(models.TextChoices):
    CHILDREN_CLOTHING = 'children_clothing', '童装'
    CRYSTAL_BRACELET = 'crystal_bracelet', '水晶手串'
    EARRINGS = 'earrings', '耳钉耳饰'
    NECKLACE = 'necklace', '项链'
    RING = 'ring', '戒指'
    BAGS = 'bags', '箱包'
    SHOES = 'shoes', '鞋类'
    COSMETICS = 'cosmetics', '化妆品'
    HOME = 'home', '家居用品'
    FOOD = 'food', '食品'
    ELECTRONICS = 'electronics', '电子产品'
    CLOTHING = 'clothing', '服装'
    ACCESSORIES = 'accessories', '配饰'
    OTHER = 'other', '其他'


class Company(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name='企业名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='企业编号')
    address = models.CharField(max_length=500, blank=True, null=True, verbose_name='企业地址')
    contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系人姓名')
    contact_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='联系电话')
    is_active = models.BooleanField(default=True, verbose_name='是否可用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'company'
        verbose_name = '企业'
        verbose_name_plural = '企业'

    def __str__(self):
        return self.name


class UserType(models.TextChoices):
    SUPER_ADMIN = 'super_admin', '网站超级管理员'
    SITE_ADMIN = 'site_admin', '网站管理员'
    ENTERPRISE_LEADER = 'enterprise_leader', '企业负责人'
    ENTERPRISE_ADMIN = 'enterprise_admin', '企业用户管理员'
    ENTERPRISE_USER = 'enterprise_user', '企业用户普通账户'
    TEMPORARY = 'temporary', '临时账户'


class User(AbstractUser):
    uid = models.UUIDField(
        verbose_name='用户唯一ID',
        unique=True,
        null=True,
        blank=True
    )
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        default=UserType.TEMPORARY,
        verbose_name='用户类型'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='所属企业'
    )
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name='创建人'
    )
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='联系电话')
    real_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='真实姓名')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')

    class Meta:
        db_table = 'user'
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def save(self, *args, **kwargs):
        if not self.uid:
            self.uid = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.username} ({self.get_user_type_display()})'


class PageConfig(models.Model):
    user_type = models.CharField(
        max_length=20,
        choices=UserType.choices,
        verbose_name='用户类型'
    )
    page_name = models.CharField(max_length=100, verbose_name='页面名称')
    page_route = models.CharField(max_length=200, verbose_name='页面路由')
    is_visible = models.BooleanField(default=True, verbose_name='是否可见')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'page_config'
        verbose_name = '页面配置'
        verbose_name_plural = '页面配置'
        unique_together = ('user_type', 'page_route')
        ordering = ['order']

    def __str__(self):
        return f'{self.get_user_type_display()} - {self.page_name}'


class Store(models.Model):
    name = models.CharField(max_length=200, verbose_name='店铺名称')
    platform = models.CharField(
        max_length=20,
        choices=Platform.choices,
        verbose_name='电商平台'
    )
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        verbose_name='店铺品类'
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='stores',
        verbose_name='所属企业'
    )
    managers = models.ManyToManyField(
        User,
        related_name='managed_stores',
        blank=True,
        verbose_name='店铺管理员'
    )
    description = models.TextField(blank=True, null=True, verbose_name='店铺描述')
    shop_url = models.URLField(blank=True, null=True, verbose_name='店铺链接')
    contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系人姓名')
    contact_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='联系电话')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_stores',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'store'
        verbose_name = '店铺'
        verbose_name_plural = '店铺'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.get_platform_display()})'
