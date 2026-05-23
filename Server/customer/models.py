from django.db import models
from company.models import Company
from account.models import User
from store.models import Product


class Customer(models.Model):
    name = models.CharField(max_length=200, verbose_name='客户名称')
    phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='联系电话')
    email = models.EmailField(blank=True, null=True, verbose_name='邮箱')
    address = models.TextField(blank=True, null=True, verbose_name='地址')
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='customers',
        verbose_name='所属企业'
    )
    contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='联系人')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_customers',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'customer'
        verbose_name = '客户'
        verbose_name_plural = '客户'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class CustomerVisibility(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='visibilities',
        verbose_name='客户'
    )
    visible_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='visible_customers',
        verbose_name='可见用户'
    )
    configured_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='configured_visibilities',
        verbose_name='配置人'
    )
    configured_at = models.DateTimeField(auto_now_add=True, verbose_name='配置时间')

    class Meta:
        db_table = 'customer_visibility'
        verbose_name = '客户可见性'
        verbose_name_plural = '客户可见性'
        unique_together = ['customer', 'visible_user']
        ordering = ['-configured_at']

    def __str__(self):
        return f'{self.customer.name} - {self.visible_user.username}'


class CustomerProduct(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='客户'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='customer_products',
        verbose_name='商品'
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='价格')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'customer_product'
        verbose_name = '客户商品'
        verbose_name_plural = '客户商品'
        unique_together = ['customer', 'product']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.customer.name} - {self.product.name}'


class CustomerPriceHistory(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='price_histories',
        verbose_name='客户'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='customer_price_histories',
        verbose_name='商品'
    )
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='价格')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_price_histories',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'customer_price_history'
        verbose_name = '报价历史'
        verbose_name_plural = '报价历史'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.customer.name} - {self.product.name} - {self.price}'
