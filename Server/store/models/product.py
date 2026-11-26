from django.db import models
from company.models import Company
from account.models import User


class ProductType(models.TextChoices):
    BEAD = 'bead', '串珠'
    ACCESSORY = 'accessory', '手串配件'
    FINISHED = 'finished', '手串成品'
    CHILDREN_CLOTHING = 'children_clothing', '童装'


class Product(models.Model):
    code = models.CharField(max_length=100, unique=True, verbose_name='货号')
    name = models.CharField(max_length=200, verbose_name='商品名称')
    product_type = models.CharField(
        max_length=20,
        choices=ProductType.choices,
        verbose_name='商品类型'
    )
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name='采购成本(元/克)')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='单颗成本')
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='售卖价格')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='库位')
    supplier = models.CharField(max_length=200, blank=True, null=True, verbose_name='供应商')
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='所属企业'
    )
    image = models.ImageField(
        upload_to='products/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='商品图片'
    )
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_products',
        verbose_name='创建人'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product'
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} - {self.name}'


class ProductSku(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='skus',
        verbose_name='关联商品'
    )
    sku_code = models.CharField(max_length=100, blank=True, default='', verbose_name='SKU编码')
    name = models.CharField(max_length=200, blank=True, default='', verbose_name='SKU名称')
    material = models.CharField(max_length=100, blank=True, null=True, verbose_name='材质')
    size = models.IntegerField(blank=True, null=True, verbose_name='规格')
    color = models.CharField(max_length=100, blank=True, null=True, verbose_name='颜色')
    purchase_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0, verbose_name='采购成本(元/克)')
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='成本价格')
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='克重')
    quality_level = models.IntegerField(default=5, verbose_name='品质等级(1-10)')
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='售卖价格')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='库位')
    supplier = models.CharField(max_length=200, blank=True, null=True, verbose_name='供应商')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')
    is_default = models.BooleanField(default=False, verbose_name='默认SKU')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'product_sku'
        verbose_name = '商品SKU'
        verbose_name_plural = '商品SKU'
        ordering = ['product_id', '-is_default', 'id']

    def __str__(self):
        label = self.name or self.sku_code or str(self.id)
        return f'{self.product.code} - {label}'


class Bead(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='关联商品'
    )
    # 串珠特有属性
    material = models.CharField(max_length=100, blank=True, null=True, verbose_name='材质')
    size = models.IntegerField(blank=True, null=True, verbose_name='规格')
    color = models.CharField(max_length=100, blank=True, null=True, verbose_name='颜色')
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='单颗克重')
    quality_level = models.IntegerField(default=5, verbose_name='品质等级(1-10)')
    remark = models.TextField(blank=True, null=True, verbose_name='备注')

    class Meta:
        db_table = 'bead'
        verbose_name = '串珠'
        verbose_name_plural = '串珠'

    def __str__(self):
        return f'串珠: {self.product.name}'


class Accessory(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='关联商品'
    )
    # 配件特有属性
    material = models.CharField(max_length=100, blank=True, null=True, verbose_name='材质')
    size = models.IntegerField(blank=True, null=True, verbose_name='规格')
    color = models.CharField(max_length=100, blank=True, null=True, verbose_name='颜色')

    class Meta:
        db_table = 'accessory'
        verbose_name = '手串配件'
        verbose_name_plural = '手串配件'

    def __str__(self):
        return f'配件: {self.product.name}'


class FinishedProduct(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='关联商品'
    )
    labor_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='工费'
    )
    elastic_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='弹性成本'
    )

    class Meta:
        db_table = 'finished_product'
        verbose_name = '手串成品'
        verbose_name_plural = '手串成品'

    def __str__(self):
        return f'成品: {self.product.name}'


class ChildrenClothing(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='关联商品'
    )
    fabric = models.CharField(max_length=100, blank=True, null=True, verbose_name='面料')
    size = models.CharField(max_length=50, blank=True, null=True, verbose_name='尺码')
    color = models.CharField(max_length=100, blank=True, null=True, verbose_name='颜色')
    season = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[('spring', '春'), ('summer', '夏'), ('autumn', '秋'), ('winter', '冬')],
        verbose_name='季节'
    )
    gender = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[('boy', '男童'), ('girl', '女童'), ('unisex', '中性')],
        verbose_name='性别'
    )
    age_range = models.CharField(max_length=50, blank=True, null=True, verbose_name='年龄段')

    class Meta:
        db_table = 'children_clothing'
        verbose_name = '童装'
        verbose_name_plural = '童装'

    def __str__(self):
        return f'童装: {self.product.name}'


class FinishedProductBead(models.Model):
    finished_product = models.ForeignKey(
        FinishedProduct,
        on_delete=models.CASCADE,
        related_name='beads',
        verbose_name='所属成品'
    )
    bead = models.ForeignKey(
        Bead,
        on_delete=models.PROTECT,
        related_name='finished_products',
        verbose_name='串珠'
    )
    sku = models.ForeignKey(
        ProductSku,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='finished_bead_items',
        verbose_name='串珠SKU'
    )
    quantity = models.IntegerField(verbose_name='数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finished_product_bead'
        verbose_name = '成品串珠组成'
        verbose_name_plural = '成品串珠组成'
        unique_together = ['finished_product', 'bead', 'sku']

    def __str__(self):
        return f'{self.finished_product.product.name} - {self.bead.product.name} x {self.quantity}'


class FinishedProductAccessory(models.Model):
    finished_product = models.ForeignKey(
        FinishedProduct,
        on_delete=models.CASCADE,
        related_name='accessories',
        verbose_name='所属成品'
    )
    accessory = models.ForeignKey(
        Accessory,
        on_delete=models.PROTECT,
        related_name='finished_products',
        verbose_name='配件'
    )
    sku = models.ForeignKey(
        ProductSku,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='finished_accessory_items',
        verbose_name='配件SKU'
    )
    quantity = models.IntegerField(verbose_name='数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'finished_product_accessory'
        verbose_name = '成品配件组成'
        verbose_name_plural = '成品配件组成'
        unique_together = ['finished_product', 'accessory', 'sku']

    def __str__(self):
        return f'{self.finished_product.product.name} - {self.accessory.product.name} x {self.quantity}'


class FinishedProductCostHistory(models.Model):
    finished_product = models.ForeignKey(
        FinishedProduct,
        on_delete=models.CASCADE,
        related_name='cost_history',
        verbose_name='关联成品'
    )
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='总成本')
    bead_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='串珠成本小计')
    accessory_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='配件成本小计')
    labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='工费')
    elastic_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='弹性成本')
    trigger_reason = models.CharField(max_length=500, blank=True, null=True, verbose_name='触发原因')
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='finished_cost_histories',
        verbose_name='触发人'
    )
    bom_snapshot = models.JSONField(default=dict, blank=True, verbose_name='BOM快照')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')

    class Meta:
        db_table = 'finished_product_cost_history'
        verbose_name = '成品成本历史'
        verbose_name_plural = '成品成本历史'
        ordering = ['finished_product_id', 'created_at']

    def __str__(self):
        return f'{self.finished_product.product.name} - {self.cost_price}'
