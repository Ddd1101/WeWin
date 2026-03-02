# Generated manually for order app
import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("store", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Buyer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4, unique=True, verbose_name="买家唯一ID"
                    ),
                ),
                (
                    "platform_user_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="平台用户ID"
                    ),
                ),
                (
                    "platform_login_id",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="平台登录ID"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="买家姓名"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="联系电话"
                    ),
                ),
                (
                    "company_name",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="公司名称"
                    ),
                ),
                (
                    "im_id",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="平台即时通讯ID"
                    ),
                ),
                (
                    "level",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="买家等级"
                    ),
                ),
                (
                    "alipay_id",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="支付宝ID"
                    ),
                ),
                ("tags", models.JSONField(blank=True, default=list, verbose_name="标签")),
                ("total_orders", models.IntegerField(default=0, verbose_name="总订单数")),
                (
                    "total_amount",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="总消费金额"
                    ),
                ),
                (
                    "first_order_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="首次下单时间"),
                ),
                (
                    "last_order_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="最后下单时间"),
                ),
                (
                    "ext_data",
                    models.JSONField(blank=True, default=dict, verbose_name="扩展数据"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buyers",
                        to="store.store",
                        verbose_name="所属店铺",
                    ),
                ),
            ],
            options={
                "verbose_name": "买家",
                "verbose_name_plural": "买家",
                "db_table": "buyer",
                "ordering": ["-created_at"],
                "unique_together": {("store", "platform_user_id")},
            },
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4, unique=True, verbose_name="订单唯一ID"
                    ),
                ),
                (
                    "platform_order_id",
                    models.CharField(
                        max_length=100, unique=True, verbose_name="平台订单ID"
                    ),
                ),
                (
                    "platform_order_id_str",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="平台订单ID字符串"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waitbuyerpay", "等待买家付款"),
                            ("waitbuyerconfirmpay", "等待买家确认付款"),
                            ("waitsellersend", "等待卖家发货"),
                            ("waitbuyerreceive", "等待买家收货"),
                            ("success", "交易成功"),
                            ("cancelled", "交易取消"),
                            ("refunding", "退款中"),
                            ("refunded", "已退款"),
                        ],
                        default="waitbuyerpay",
                        max_length=50,
                        verbose_name="订单状态",
                    ),
                ),
                (
                    "status_str",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="状态字符串"
                    ),
                ),
                (
                    "total_amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="订单总金额"
                    ),
                ),
                (
                    "sum_product_payment",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="商品总金额"
                    ),
                ),
                (
                    "discount",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="折扣金额"
                    ),
                ),
                (
                    "shipping_fee",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="运费"
                    ),
                ),
                (
                    "refund_amount",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="退款金额"
                    ),
                ),
                (
                    "refund_payment",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                        verbose_name="退款支付金额",
                    ),
                ),
                (
                    "business_type",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="业务类型"
                    ),
                ),
                (
                    "trade_type",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="交易类型"
                    ),
                ),
                (
                    "flow_template_code",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="交易流程模板代码"
                    ),
                ),
                ("step_pay_all", models.BooleanField(default=False, verbose_name="是否分步付款")),
                ("over_sea_order", models.BooleanField(default=False, verbose_name="是否海外订单")),
                ("seller_order", models.BooleanField(default=False, verbose_name="是否卖家订单")),
                (
                    "alipay_trade_id",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="支付宝交易ID"
                    ),
                ),
                (
                    "seller_user_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="卖家用户ID"
                    ),
                ),
                (
                    "seller_login_id",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="卖家登录ID"
                    ),
                ),
                (
                    "seller_alipay_id",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="卖家支付宝ID"
                    ),
                ),
                (
                    "platform_create_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="平台创建时间"),
                ),
                (
                    "platform_pay_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="平台付款时间"),
                ),
                (
                    "platform_modify_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="平台修改时间"),
                ),
                (
                    "all_delivered_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="全部发货时间"),
                ),
                (
                    "receiver_name",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="收货人姓名"
                    ),
                ),
                (
                    "receiver_phone",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="收货人电话"
                    ),
                ),
                (
                    "receiver_province",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="收货省份"
                    ),
                ),
                (
                    "receiver_city",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="收货城市"
                    ),
                ),
                (
                    "receiver_area",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="收货地区"
                    ),
                ),
                (
                    "receiver_address",
                    models.TextField(blank=True, null=True, verbose_name="收货详细地址"),
                ),
                (
                    "receiver_zip",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="收货邮编"
                    ),
                ),
                (
                    "receiver_division_code",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="收货地址编码"
                    ),
                ),
                (
                    "buyer_rate_status",
                    models.IntegerField(blank=True, null=True, verbose_name="买家评价状态"),
                ),
                (
                    "seller_rate_status",
                    models.IntegerField(blank=True, null=True, verbose_name="卖家评价状态"),
                ),
                (
                    "ext_data",
                    models.JSONField(blank=True, default=dict, verbose_name="扩展数据"),
                ),
                (
                    "raw_data",
                    models.JSONField(blank=True, default=dict, verbose_name="原始数据"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "buyer",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="orders",
                        to="order.buyer",
                        verbose_name="买家",
                    ),
                ),
                (
                    "store",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to="store.store",
                        verbose_name="所属店铺",
                    ),
                ),
            ],
            options={
                "verbose_name": "订单",
                "verbose_name_plural": "订单",
                "db_table": "order",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderItem",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4, unique=True, verbose_name="订单项唯一ID"
                    ),
                ),
                (
                    "platform_sub_order_id",
                    models.CharField(max_length=100, verbose_name="平台子订单ID"),
                ),
                (
                    "platform_sub_order_id_str",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="平台子订单ID字符串"
                    ),
                ),
                (
                    "product_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="商品ID"
                    ),
                ),
                ("product_name", models.CharField(max_length=500, verbose_name="商品名称")),
                (
                    "product_cargo_number",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="商品货号"
                    ),
                ),
                (
                    "product_img_urls",
                    models.JSONField(blank=True, default=list, verbose_name="商品图片URL"),
                ),
                (
                    "product_snapshot_url",
                    models.URLField(blank=True, null=True, verbose_name="商品快照URL"),
                ),
                (
                    "sku_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="SKU ID"
                    ),
                ),
                (
                    "spec_id",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="规格ID"
                    ),
                ),
                (
                    "sku_infos",
                    models.JSONField(blank=True, default=list, verbose_name="SKU信息"),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="商品价格"
                    ),
                ),
                ("quantity", models.IntegerField(verbose_name="数量")),
                (
                    "quantity_factor",
                    models.DecimalField(
                        decimal_places=2, default=1, max_digits=10, verbose_name="数量因子"
                    ),
                ),
                (
                    "item_amount",
                    models.DecimalField(
                        decimal_places=2, max_digits=12, verbose_name="商品金额"
                    ),
                ),
                (
                    "entry_discount",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="入口折扣"
                    ),
                ),
                (
                    "refund",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="退款金额"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waitbuyerpay", "等待买家付款"),
                            ("waitbuyerconfirmpay", "等待买家确认付款"),
                            ("waitsellersend", "等待卖家发货"),
                            ("waitbuyerreceive", "等待买家收货"),
                            ("success", "交易成功"),
                            ("cancelled", "交易取消"),
                            ("refunding", "退款中"),
                            ("refunded", "已退款"),
                        ],
                        default="waitbuyerpay",
                        max_length=50,
                        verbose_name="状态",
                    ),
                ),
                (
                    "status_str",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="状态字符串"
                    ),
                ),
                (
                    "logistics_status",
                    models.IntegerField(blank=True, null=True, verbose_name="物流状态"),
                ),
                (
                    "item_type",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="类型"
                    ),
                ),
                (
                    "unit",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="单位"
                    ),
                ),
                (
                    "platform_create_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="平台创建时间"),
                ),
                (
                    "platform_modify_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="平台修改时间"),
                ),
                (
                    "ext_data",
                    models.JSONField(blank=True, default=dict, verbose_name="扩展数据"),
                ),
                (
                    "raw_data",
                    models.JSONField(blank=True, default=dict, verbose_name="原始数据"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="order.order",
                        verbose_name="所属订单",
                    ),
                ),
            ],
            options={
                "verbose_name": "订单项",
                "verbose_name_plural": "订单项",
                "db_table": "order_item",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderLogistics",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4, unique=True, verbose_name="物流唯一ID"
                    ),
                ),
                (
                    "platform_logistics_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="平台物流ID"
                    ),
                ),
                (
                    "logistics_code",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="物流编码"
                    ),
                ),
                (
                    "logistics_company_id",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="物流公司ID"
                    ),
                ),
                (
                    "logistics_company_no",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="物流公司编号"
                    ),
                ),
                (
                    "logistics_bill_no",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="物流单号"
                    ),
                ),
                (
                    "logistics_type",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="物流类型"
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("waitsend", "待发货"),
                            ("alreadysend", "已发货"),
                            ("signed", "已签收"),
                            ("returned", "已退回"),
                        ],
                        default="waitsend",
                        max_length=50,
                        verbose_name="物流状态",
                    ),
                ),
                (
                    "delivered_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="发货时间"),
                ),
                (
                    "from_province",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="出发省份"
                    ),
                ),
                (
                    "from_city",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="出发城市"
                    ),
                ),
                (
                    "from_area",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="出发地区"
                    ),
                ),
                (
                    "from_address",
                    models.TextField(blank=True, null=True, verbose_name="出发地址"),
                ),
                (
                    "from_phone",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="出发地电话"
                    ),
                ),
                (
                    "from_post",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="出发地邮编"
                    ),
                ),
                (
                    "to_province",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="目的省份"
                    ),
                ),
                (
                    "to_city",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="目的城市"
                    ),
                ),
                (
                    "to_area",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="目的地区"
                    ),
                ),
                (
                    "to_address",
                    models.TextField(blank=True, null=True, verbose_name="目的地址"),
                ),
                (
                    "to_post",
                    models.CharField(
                        blank=True, max_length=20, null=True, verbose_name="目的邮编"
                    ),
                ),
                (
                    "no_logistics_condition",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="无需物流条件"
                    ),
                ),
                (
                    "no_logistics_name",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="无需物流名称"
                    ),
                ),
                (
                    "no_logistics_tel",
                    models.CharField(
                        blank=True, max_length=50, null=True, verbose_name="无需物流电话"
                    ),
                ),
                (
                    "no_logistics_bill_no",
                    models.CharField(
                        blank=True, max_length=200, null=True, verbose_name="无需物流单号"
                    ),
                ),
                (
                    "sub_item_ids",
                    models.TextField(blank=True, null=True, verbose_name="子订单ID列表"),
                ),
                (
                    "platform_create_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="平台创建时间"),
                ),
                (
                    "platform_modify_time",
                    models.DateTimeField(blank=True, null=True, verbose_name="平台修改时间"),
                ),
                (
                    "ext_data",
                    models.JSONField(blank=True, default=dict, verbose_name="扩展数据"),
                ),
                (
                    "raw_data",
                    models.JSONField(blank=True, default=dict, verbose_name="原始数据"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="logistics",
                        to="order.order",
                        verbose_name="所属订单",
                    ),
                ),
            ],
            options={
                "verbose_name": "订单物流",
                "verbose_name_plural": "订单物流",
                "db_table": "order_logistics",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="OrderStep",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "uid",
                    models.UUIDField(
                        default=uuid.uuid4, unique=True, verbose_name="步骤唯一ID"
                    ),
                ),
                ("step_no", models.IntegerField(verbose_name="步骤编号")),
                ("step_name", models.CharField(max_length=200, verbose_name="步骤名称")),
                ("is_last_step", models.BooleanField(default=False, verbose_name="是否最后一步")),
                (
                    "active_status",
                    models.IntegerField(blank=True, null=True, verbose_name="活动状态"),
                ),
                (
                    "pay_status",
                    models.IntegerField(blank=True, null=True, verbose_name="付款状态"),
                ),
                (
                    "logistics_status",
                    models.IntegerField(blank=True, null=True, verbose_name="物流状态"),
                ),
                (
                    "pay_fee",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="付款费用"
                    ),
                ),
                (
                    "paid_fee",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="已付费用"
                    ),
                ),
                (
                    "adjust_fee",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="调整费用"
                    ),
                ),
                (
                    "discount_fee",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="折扣费用"
                    ),
                ),
                (
                    "post_fee",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="邮费"
                    ),
                ),
                (
                    "paid_post_fee",
                    models.DecimalField(
                        decimal_places=2, default=0, max_digits=12, verbose_name="已付邮费"
                    ),
                ),
                (
                    "gmt_start",
                    models.DateTimeField(blank=True, null=True, verbose_name="开始时间"),
                ),
                (
                    "gmt_pay",
                    models.DateTimeField(blank=True, null=True, verbose_name="付款时间"),
                ),
                (
                    "ext_data",
                    models.JSONField(blank=True, default=dict, verbose_name="扩展数据"),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="创建时间"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="更新时间"),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="steps",
                        to="order.order",
                        verbose_name="所属订单",
                    ),
                ),
            ],
            options={
                "verbose_name": "订单步骤",
                "verbose_name_plural": "订单步骤",
                "db_table": "order_step",
                "ordering": ["step_no"],
            },
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["store", "status"], name="order_store_i_c41e4b_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(
                fields=["store", "platform_create_time"],
                name="order_store_i_a78c7b_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["buyer"], name="order_buyer_i_8ea383_idx"),
        ),
    ]
