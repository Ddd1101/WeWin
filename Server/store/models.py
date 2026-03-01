from django.db import models
from company.models import Company
from account.models import User
import uuid
import json


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


class OrderStatus(models.TextChoices):
    WAIT_BUYER_PAY = 'waitbuyerpay', '等待买家付款'
    WAIT_SELLER_SEND = 'waitsellersend', '等待卖家发货'
    WAIT_BUYER_RECEIVE = 'waitbuyerreceive', '等待买家确认收货'
    SUCCESS = 'success', '交易成功'
    CANCEL = 'cancel', '交易关闭'
    PAID_BUT_NOT_FUND = 'paid_but_not_fund', '已支付，未到账'
    CONFIRM_GOODS = 'confirm_goods', '已收货'
    WAIT_SELLER_CONFIRM = 'waitsellerconfirm', '等待卖家确认订单'
    WAIT_BUYER_CONFIRM = 'waitbuyerconfirm', '等待买家确认订单'
    CONFIRM_GOODS_BUT_NOT_FUND = 'confirm_goods_but_not_fund', '已收货，未到账'
    CONFIRM_GOODS_AND_HAS_SUBSIDY = 'confirm_goods_and_has_subsidy', '已收货，已贴现'
    SEND_GOODS_BUT_NOT_FUND = 'send_goods_but_not_fund', '已发货，未到账'
    WAIT_LOGISTICS_TAKEIN = 'waitlogisticstakein', '等待物流揽件'
    WAIT_BUYER_SIGN = 'waitbuyersign', '等待买家签收'
    SIGN_SUCCESS = 'signinsuccess', '买家已签收'
    SIGN_FAILED = 'signinfailed', '签收失败'
    WAIT_SELLER_ACT = 'waitselleract', '等待卖家操作'
    WAIT_BUYER_CONFIRM_ACTION = 'waitbuyerconfirmaction', '等待买家确认操作'
    WAIT_SELLER_PUSH = 'waitsellerpush', '等待卖家推进'


class RefundStatus(models.TextChoices):
    NO_REFUND = 'no_refund', '无退款'
    WAIT_SELLER_AGREE = 'waitselleragree', '等待卖家同意'
    REFUND_SUCCESS = 'refundsuccess', '退款成功'


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


class PlatformApiConfig(models.Model):
    store = models.OneToOneField(
        Store,
        on_delete=models.CASCADE,
        related_name='api_config',
        verbose_name='关联店铺'
    )
    app_key = models.CharField(max_length=100, blank=True, null=True, verbose_name='App Key')
    app_secret = models.CharField(max_length=200, blank=True, null=True, verbose_name='App Secret')
    access_token = models.TextField(blank=True, null=True, verbose_name='Access Token')
    refresh_token = models.TextField(blank=True, null=True, verbose_name='Refresh Token')
    token_expires_at = models.DateTimeField(blank=True, null=True, verbose_name='Token过期时间')
    extra_config = models.JSONField(default=dict, blank=True, verbose_name='扩展配置')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'platform_api_config'
        verbose_name = '平台API配置'
        verbose_name_plural = '平台API配置'

    def __str__(self):
        return f'{self.store.name} API配置'


class Order(models.Model):
    id = models.BigAutoField(primary_key=True)
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='所属店铺'
    )
    platform_order_id = models.CharField(max_length=100, verbose_name='平台订单ID')
    platform_order_no = models.CharField(max_length=100, blank=True, null=True, verbose_name='平台订单号')
    order_status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        verbose_name='订单状态'
    )
    refund_status = models.CharField(
        max_length=30,
        choices=RefundStatus.choices,
        default=RefundStatus.NO_REFUND,
        verbose_name='退款状态'
    )
    buyer_login_id = models.CharField(max_length=200, blank=True, null=True, verbose_name='买家账号')
    buyer_open_uid = models.CharField(max_length=200, blank=True, null=True, verbose_name='买家Open UID')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='订单总额')
    sum_product_payment = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='商品总额')
    shipping_fee = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='运费')
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='折扣')
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='退款金额')
    create_time = models.DateTimeField(verbose_name='订单创建时间')
    pay_time = models.DateTimeField(blank=True, null=True, verbose_name='支付时间')
    modify_time = models.DateTimeField(blank=True, null=True, verbose_name='修改时间')
    seller_remark_icon = models.CharField(max_length=10, blank=True, null=True, verbose_name='卖家备注图标')
    seller_memo = models.TextField(blank=True, null=True, verbose_name='卖家备注')
    buyer_memo = models.TextField(blank=True, null=True, verbose_name='买家备注')
    alipay_trade_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='支付宝交易号')
    trade_type = models.CharField(max_length=20, blank=True, null=True, verbose_name='交易类型')
    flow_template_code = models.CharField(max_length=50, blank=True, null=True, verbose_name='流程模板代码')
    business_type = models.CharField(max_length=20, blank=True, null=True, verbose_name='业务类型')
    can_send_goods = models.BooleanField(default=True, verbose_name='是否可发货')
    cant_send_reason = models.CharField(max_length=200, blank=True, null=True, verbose_name='不可发货原因')
    platform_raw_data = models.JSONField(default=dict, blank=True, verbose_name='平台原始数据')
    synced_at = models.DateTimeField(auto_now_add=True, verbose_name='同步时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'order'
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-create_time']
        unique_together = ['store', 'platform_order_id']
        indexes = [
            models.Index(fields=['store', 'order_status']),
            models.Index(fields=['create_time']),
            models.Index(fields=['platform_order_id']),
        ]

    def __str__(self):
        return f'{self.store.name} - {self.platform_order_id}'


class OrderItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='所属订单'
    )
    platform_item_id = models.CharField(max_length=100, verbose_name='平台子订单ID')
    product_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='商品ID')
    product_name = models.CharField(max_length=500, verbose_name='商品名称')
    product_img_url = models.TextField(blank=True, null=True, verbose_name='商品图片URL')
    product_snapshot_url = models.URLField(blank=True, null=True, verbose_name='商品快照URL')
    product_cargo_number = models.CharField(max_length=200, blank=True, null=True, verbose_name='商品货号')
    sku_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='SKU ID')
    sku_specs = models.JSONField(default=list, blank=True, verbose_name='SKU规格')
    quantity = models.IntegerField(verbose_name='数量')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='单价')
    item_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='商品金额')
    entry_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name='子订单折扣')
    unit = models.CharField(max_length=20, blank=True, null=True, verbose_name='单位')
    item_status = models.CharField(
        max_length=50,
        choices=OrderStatus.choices,
        blank=True,
        null=True,
        verbose_name='子订单状态'
    )
    item_refund_status = models.CharField(
        max_length=30,
        choices=RefundStatus.choices,
        default=RefundStatus.NO_REFUND,
        verbose_name='子订单退款状态'
    )
    refund_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='退款单ID')
    guarantees_terms = models.JSONField(default=list, blank=True, verbose_name='保障条款')
    logistics_status = models.IntegerField(blank=True, null=True, verbose_name='物流状态')
    gmt_create = models.DateTimeField(blank=True, null=True, verbose_name='创建时间')
    gmt_modified = models.DateTimeField(blank=True, null=True, verbose_name='修改时间')
    platform_raw_data = models.JSONField(default=dict, blank=True, verbose_name='平台原始数据')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'order_item'
        verbose_name = '订单商品'
        verbose_name_plural = '订单商品'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['platform_item_id']),
        ]

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'


class OrderReceiver(models.Model):
    id = models.BigAutoField(primary_key=True)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='receiver',
        verbose_name='所属订单'
    )
    receiver_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='收货人姓名')
    receiver_phone = models.CharField(max_length=50, blank=True, null=True, verbose_name='收货人电话')
    receiver_mobile = models.CharField(max_length=50, blank=True, null=True, verbose_name='收货人手机')
    province = models.CharField(max_length=100, blank=True, null=True, verbose_name='省份')
    city = models.CharField(max_length=100, blank=True, null=True, verbose_name='城市')
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name='区县')
    address = models.TextField(blank=True, null=True, verbose_name='详细地址')
    zip_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='邮编')
    to_division_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='收货地址编码')
    full_address = models.TextField(blank=True, null=True, verbose_name='完整地址')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'order_receiver'
        verbose_name = '订单收货人'
        verbose_name_plural = '订单收货人'

    def __str__(self):
        return f'{self.receiver_name} - {self.full_address}'


class DataPullStatus(models.TextChoices):
    PENDING = 'pending', '待拉取'
    PULLING = 'pulling', '拉取中'
    SUCCESS = 'success', '拉取成功'
    FAILED = 'failed', '拉取失败'


class DataPullTask(models.Model):
    id = models.BigAutoField(primary_key=True)
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='pull_tasks',
        verbose_name='所属店铺'
    )
    task_type = models.CharField(max_length=50, verbose_name='任务类型')
    status = models.CharField(
        max_length=20,
        choices=DataPullStatus.choices,
        default=DataPullStatus.PENDING,
        verbose_name='状态'
    )
    start_time = models.DateTimeField(blank=True, null=True, verbose_name='拉取开始时间')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name='拉取结束时间')
    order_count = models.IntegerField(default=0, verbose_name='拉取订单数')
    new_order_count = models.IntegerField(default=0, verbose_name='新增订单数')
    updated_order_count = models.IntegerField(default=0, verbose_name='更新订单数')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    params = models.JSONField(default=dict, blank=True, verbose_name='任务参数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'data_pull_task'
        verbose_name = '数据拉取任务'
        verbose_name_plural = '数据拉取任务'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.store.name} - {self.get_task_type_display()} - {self.get_status_display()}'


class StoreDataConfig(models.Model):
    store = models.OneToOneField(
        Store,
        on_delete=models.CASCADE,
        related_name='data_config',
        verbose_name='关联店铺'
    )
    auto_pull_enabled = models.BooleanField(default=False, verbose_name='是否自动拉取')
    pull_interval_hours = models.IntegerField(default=1, verbose_name='拉取间隔(小时)')
    last_pull_time = models.DateTimeField(blank=True, null=True, verbose_name='上次拉取时间')
    next_pull_time = models.DateTimeField(blank=True, null=True, verbose_name='下次拉取时间')
    pull_status = models.CharField(
        max_length=20,
        choices=DataPullStatus.choices,
        default=DataPullStatus.PENDING,
        verbose_name='拉取状态'
    )
    extra_config = models.JSONField(default=dict, blank=True, verbose_name='扩展配置')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'store_data_config'
        verbose_name = '店铺数据配置'
        verbose_name_plural = '店铺数据配置'

    def __str__(self):
        return f'{self.store.name} 数据配置'


class StoreData(models.Model):
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='data_records',
        verbose_name='所属店铺'
    )
    data_type = models.CharField(max_length=50, verbose_name='数据类型')
    data_date = models.DateField(verbose_name='数据日期')
    data_value = models.JSONField(default=dict, blank=True, verbose_name='数据值')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'store_data'
        verbose_name = '店铺数据记录'
        verbose_name_plural = '店铺数据记录'
        unique_together = ['store', 'data_type', 'data_date']
        ordering = ['-data_date', '-created_at']

    def __str__(self):
        return f'{self.store.name} - {self.data_type} - {self.data_date}'
