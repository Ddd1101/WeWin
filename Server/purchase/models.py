from django.db import models
from decimal import Decimal
from company.models import Company
from account.models import User
from store.models import Product, ProductSku


class PurchaseListStatus(models.TextChoices):
    PENDING = 'pending', '待采购'
    IN_PROGRESS = 'in_progress', '进行中'
    COMPLETED = 'completed', '已完成'


class PurchaseItemStatus(models.TextChoices):
    PENDING = 'pending', '待采购'
    PARTIALLY_PURCHASED = 'partially_purchased', '已购买部分'
    PURCHASED = 'purchased', '已购买'


class PurchaseList(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='purchase_lists',
        null=True,
        blank=True,
        verbose_name='所属企业'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_purchase_lists',
        verbose_name='创建人'
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_purchase_lists',
        verbose_name='采购负责人'
    )
    title = models.CharField(max_length=200, verbose_name='清单标题')
    status = models.CharField(
        max_length=20,
        choices=PurchaseListStatus.choices,
        default=PurchaseListStatus.PENDING,
        verbose_name='清单状态'
    )
    planned_date = models.DateField(verbose_name='计划采购日期')
    notes = models.TextField(blank=True, default='', verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_list'
        verbose_name = '采购清单'
        verbose_name_plural = '采购清单'
        ordering = ['-planned_date', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.planned_date})"


class PurchaseItem(models.Model):
    purchase_list = models.ForeignKey(
        PurchaseList,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='所属采购清单'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_items',
        verbose_name='关联商品'
    )
    sku = models.ForeignKey(
        ProductSku,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='purchase_items',
        verbose_name='关联SKU'
    )
    product_type = models.CharField(max_length=20, verbose_name='商品类型')  # bead/accessory
    product_name = models.CharField(max_length=200, blank=True, default='', verbose_name='商品名称')
    sku_code = models.CharField(max_length=100, blank=True, default='', verbose_name='SKU编码')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='采购数量')
    unit = models.CharField(max_length=10, default='克', verbose_name='单位')  # 克/件
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='单价'
    )
    supplier = models.CharField(max_length=200, blank=True, default='', verbose_name='供应商')
    location = models.CharField(max_length=200, blank=True, default='', verbose_name='库位')
    quality_level = models.IntegerField(null=True, blank=True, verbose_name='品质等级')
    material = models.CharField(max_length=100, blank=True, default='', verbose_name='材质')
    size = models.IntegerField(null=True, blank=True, verbose_name='规格')
    color = models.CharField(max_length=100, blank=True, default='', verbose_name='颜色')
    remark = models.TextField(blank=True, default='', verbose_name='备注')
    status = models.CharField(
        max_length=20,
        choices=PurchaseItemStatus.choices,
        default=PurchaseItemStatus.PENDING,
        verbose_name='采购项状态'
    )
    purchased_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0'),
        verbose_name='已购买数量'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'purchase_item'
        verbose_name = '采购项'
        verbose_name_plural = '采购项'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.product_name} x{self.quantity}{self.unit}"
