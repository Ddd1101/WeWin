import logging
from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal
from django.utils import timezone
from ..models import Order, OrderItem, OrderLogistics, OrderStep, Buyer
from store.models import Store

logger = logging.getLogger(__name__)


class OrderProcessor:
    """订单数据处理器，将标准化的订单数据保存到数据库"""

    def __init__(self, store: Store):
        self.store = store

    def parse_timestamp(self, timestamp_str: Optional[str]) -> Optional[datetime]:
        """
        解析1688时间戳格式
        :param timestamp_str: 时间戳字符串，如 '20240101123456789+0800'
        :return: datetime对象
        """
        if not timestamp_str:
            return None
        try:
            dt = datetime.strptime(timestamp_str[:17], "%Y%m%d%H%M%S%f")
            return timezone.make_aware(dt)
        except Exception as e:
            logger.warning(f"解析时间戳失败: {timestamp_str}, 错误: {e}")
            return None

    def get_or_create_buyer(self, normalized_data: Dict) -> Optional[Buyer]:
        """
        获取或创建买家记录
        :param normalized_data: 标准化的订单数据
        :return: Buyer对象
        """
        platform_user_id = normalized_data.get("buyer_member_id", "")
        if not platform_user_id:
            return None

        buyer_contact = normalized_data.get("buyer_contact", {})
        receive_address = normalized_data.get("receive_address", {})

        buyer, created = Buyer.objects.get_or_create(
            store=self.store,
            platform_user_id=platform_user_id,
            defaults={
                "platform_login_id": normalized_data.get("buyer_login_id", ""),
                "name": receive_address.get("fullName", ""),
                "phone": receive_address.get("mobile", ""),
                "company_name": buyer_contact.get("companyName", ""),
                "im_id": buyer_contact.get("imInUserId", ""),
                "ext_data": {
                    "buyer_contact": buyer_contact,
                    "receive_address": receive_address,
                },
            }
        )

        return buyer

    def process_order(self, normalized_data: Dict) -> Optional[Order]:
        """
        处理单个订单数据并保存到数据库
        :param normalized_data: 标准化的订单数据
        :return: Order对象
        """
        platform_order_id = normalized_data.get("platform_order_id", "")
        if not platform_order_id:
            logger.warning("缺少平台订单ID，跳过处理")
            return None

        raw_data = normalized_data.get("raw_data", {})
        order_info = raw_data.get("result", {}).get("toReturn", {}).get("orderInfo", {})

        buyer = self.get_or_create_buyer(normalized_data)
        receive_address = normalized_data.get("receive_address", {})

        order, created = Order.objects.update_or_create(
            platform_order_id=platform_order_id,
            defaults={
                "store": self.store,
                "buyer": buyer,
                "status": self.map_status(normalized_data.get("status", "")),
                "status_str": normalized_data.get("status", ""),
                "total_amount": Decimal(str(normalized_data.get("total_amount", 0))),
                "sum_product_payment": Decimal(str(normalized_data.get("payment", 0))),
                "discount": Decimal(str(normalized_data.get("discount", 0))),
                "shipping_fee": Decimal(str(normalized_data.get("post_fee", 0))),
                "refund_amount": Decimal(str(order_info.get("refund", 0))),
                "business_type": order_info.get("businessType", ""),
                "trade_type": order_info.get("tradeType", ""),
                "step_pay_all": bool(order_info.get("stepPayAll", False)),
                "over_sea_order": bool(order_info.get("overSeaOrder", False)),
                "seller_order": bool(order_info.get("sellerOrder", False)),
                "alipay_trade_id": order_info.get("alipayTradeId", ""),
                "seller_user_id": order_info.get("sellerUserId", ""),
                "seller_login_id": order_info.get("sellerLoginId", ""),
                "platform_create_time": self.parse_timestamp(normalized_data.get("gmt_create")),
                "platform_pay_time": self.parse_timestamp(normalized_data.get("gmt_payment")),
                "platform_modify_time": self.parse_timestamp(normalized_data.get("gmt_modified")),
                "receiver_name": receive_address.get("fullName", ""),
                "receiver_phone": receive_address.get("mobile", ""),
                "receiver_province": receive_address.get("province", ""),
                "receiver_city": receive_address.get("city", ""),
                "receiver_area": receive_address.get("area", ""),
                "receiver_address": receive_address.get("address", ""),
                "receiver_zip": receive_address.get("post", ""),
                "ext_data": {
                    "refund": normalized_data.get("refund", {}),
                    "step_order_info": normalized_data.get("step_order_info", {}),
                },
                "raw_data": raw_data,
            }
        )

        self.process_order_items(order, normalized_data.get("order_items", []))
        self.process_order_steps(order, normalized_data.get("step_order_info", {}))

        return order

    def map_status(self, status: str) -> str:
        """
        映射1688订单状态到系统状态
        :param status: 1688订单状态
        :return: 系统订单状态
        """
        status_map = {
            "waitbuyerpay": "waitbuyerpay",
            "waitbuyerconfirmpay": "waitbuyerconfirmpay",
            "waitsellersend": "waitsellersend",
            "waitbuyerreceive": "waitbuyerreceive",
            "success": "success",
            "cancel": "cancelled",
            "cancelled": "cancelled",
            "refundsuccess": "refunded",
            "refunding": "refunding",
        }
        return status_map.get(status, status)

    def process_order_items(self, order: Order, items_data: list):
        """
        处理订单项数据
        :param order: 订单对象
        :param items_data: 订单项数据列表
        """
        for item_data in items_data:
            platform_sub_order_id = item_data.get("sku_id", "") or item_data.get("item_id", "")
            if not platform_sub_order_id:
                continue

            OrderItem.objects.update_or_create(
                order=order,
                platform_sub_order_id=platform_sub_order_id,
                defaults={
                    "product_id": item_data.get("item_id", ""),
                    "product_name": item_data.get("product_name", ""),
                    "product_cargo_number": item_data.get("item_id", ""),
                    "product_img_urls": [item_data.get("product_img_url", "")] if item_data.get("product_img_url") else [],
                    "sku_id": item_data.get("sku_id", ""),
                    "spec_id": item_data.get("spec_id", ""),
                    "price": Decimal(str(item_data.get("price", 0))),
                    "quantity": int(item_data.get("quantity", 0)),
                    "item_amount": Decimal(str(item_data.get("item_amount", 0))),
                    "status": self.map_status(order.status),
                    "status_str": order.status_str,
                    "raw_data": item_data.get("raw_data", {}),
                }
            )

    def process_order_steps(self, order: Order, step_info: Dict):
        """
        处理订单步骤数据
        :param order: 订单对象
        :param step_info: 步骤信息
        """
        steps = step_info.get("stepList", [])
        for idx, step in enumerate(steps):
            OrderStep.objects.update_or_create(
                order=order,
                step_no=idx + 1,
                defaults={
                    "step_name": step.get("stepName", ""),
                    "is_last_step": bool(step.get("lastStep", False)),
                    "active_status": step.get("activeStatus"),
                    "pay_status": step.get("payStatus"),
                    "logistics_status": step.get("logisticsStatus"),
                    "pay_fee": Decimal(str(step.get("payFee", 0))),
                    "paid_fee": Decimal(str(step.get("paidFee", 0))),
                    "discount_fee": Decimal(str(step.get("discountFee", 0))),
                    "post_fee": Decimal(str(step.get("postFee", 0))),
                    "paid_post_fee": Decimal(str(step.get("paidPostFee", 0))),
                    "gmt_start": self.parse_timestamp(step.get("gmtStart")),
                    "gmt_pay": self.parse_timestamp(step.get("gmtPay")),
                }
            )
