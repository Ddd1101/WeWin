import hmac
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
from django.db import transaction
from .base import BaseDataPullService
from ..models import (
    Order,
    OrderItem,
    OrderReceiver,
    OrderStatus,
    RefundStatus,
    DataPullStatus,
    DataPullTask,
)


class Ali1688DataPullService(BaseDataPullService):
    """
    1688平台数据拉取服务
    """

    BASE_URL = "https://gw.open.1688.com/openapi/"
    REQUEST_TYPE_TRADE = "param2/1/com.alibaba.trade/"

    def __init__(self, store):
        super().__init__(store)
        self.app_key = self.api_config.app_key if self.api_config else None
        self.app_secret = (
            self.api_config.app_secret.encode("utf-8")
            if self.api_config and self.api_config.app_secret
            else None
        )
        self.access_token = self.api_config.access_token if self.api_config else None
        self.request_logs = []

    def _calculate_signature(self, url_path: str, data: Dict[str, Any]) -> str:
        """
        计算1688 API签名

        Args:
            url_path: URL路径
            data: 请求参数

        Returns:
            签名字符串
        """
        params = []
        for key in sorted(data.keys()):
            params.append(key + str(data[key]))
        params.sort()
        assembled_params = "".join(params)
        merged_params = url_path + assembled_params
        merged_params = bytes(merged_params, "utf8")

        hex_res = hmac.new(self.app_secret, merged_params, digestmod="sha1").hexdigest()

        return hex_res.upper()

    def _format_date(self, dt: datetime) -> str:
        """
        格式化日期为1688 API要求的格式

        Args:
            dt: datetime对象

        Returns:
            格式化后的日期字符串
        """
        return dt.strftime("%Y%m%d") + "000000000+0800"

    def _de_format_time(self, date_str: str) -> Optional[datetime]:
        """
        解析1688 API返回的时间格式

        Args:
            date_str: 时间字符串

        Returns:
            datetime对象
        """
        try:
            return datetime.strptime(date_str[:-5], "%Y%m%d%H%M%S%f")
        except:
            return None

    def _get_trade_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用1688获取订单列表API

        Args:
            data: 请求参数

        Returns:
            API返回结果
        """
        if not self.app_key or not self.app_secret or not self.access_token:
            raise ValueError("API配置不完整")

        data["access_token"] = self.access_token

        url_path = (
            self.REQUEST_TYPE_TRADE + "alibaba.trade.getSellerOrderList/" + self.app_key
        )
        _aop_signature = self._calculate_signature(url_path, data)
        data["_aop_signature"] = _aop_signature

        url = self.BASE_URL + url_path

        request_info = {"url": url, "method": "POST", "params": data.copy()}

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            request_info["response"] = result
            request_info["status_code"] = response.status_code
            self.request_logs.append(request_info)
            return result
        except Exception as e:
            request_info["error"] = str(e)
            self.request_logs.append(request_info)
            raise Exception(f"API调用失败: {str(e)}")

    def _get_single_trade_detail(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个订单详情

        Args:
            order_id: 订单ID

        Returns:
            订单详情
        """
        if not self.app_key or not self.app_secret or not self.access_token:
            raise ValueError("API配置不完整")

        data = {
            "orderId": order_id,
            "access_token": self.access_token,
            "needBuyerAddressAndPhone": "true",
        }

        url_path = (
            self.REQUEST_TYPE_TRADE + "alibaba.trade.get.sellerView/" + self.app_key
        )
        _aop_signature = self._calculate_signature(url_path, data)
        data["_aop_signature"] = _aop_signature

        url = self.BASE_URL + url_path

        try:
            print("===============")
            print(url)
            print(data)
            response = requests.post(url, data=data)
            response.raise_for_status()
            result = response.json()
            if result.get("success") and result.get("result"):
                return result["result"]
            return None
        except Exception as e:
            raise Exception(f"获取订单详情失败: {str(e)}")

    def pull_orders(
        self,
        start_time: datetime,
        end_time: datetime,
        task: Optional[DataPullTask] = None,
    ) -> Dict[str, Any]:
        """
        拉取订单数据

        Args:
            start_time: 开始时间
            end_time: 结束时间
            task: 数据拉取任务

        Returns:
            拉取结果统计信息
        """
        if task:
            self.update_task_status(task, DataPullStatus.PULLING)

        stats = {
            "total_count": 0,
            "new_count": 0,
            "updated_count": 0,
            "failed_count": 0,
        }

        try:
            req_data = {
                "createStartTime": self._format_date(start_time),
                "createEndTime": self._format_date(end_time),
                "needMemoInfo": "true",
                "needBuyerAddressAndPhone": "true",
                "pageSize": 20,
            }

            res = self._get_trade_data(req_data)
            total_record = res.get("totalRecord", 0)
            page_num = (total_record + 19) // 20

            for page in range(page_num):
                req_data.pop("_aop_signature")
                req_data["page"] = str(page + 1)
                res = self._get_trade_data(req_data)

                if "result" in res:
                    for order_data in res["result"]:
                        stats["total_count"] += 1
                        try:
                            is_new = self.save_order(order_data)
                            if is_new:
                                stats["new_count"] += 1
                            else:
                                stats["updated_count"] += 1
                        except Exception as e:
                            stats["failed_count"] += 1
                            print(f"保存订单失败: {str(e)}")

            if task:
                self.update_task_status(
                    task,
                    DataPullStatus.SUCCESS,
                    order_count=stats["total_count"],
                    new_order_count=stats["new_count"],
                    updated_order_count=stats["updated_count"],
                )

        except Exception as e:
            if task:
                self.update_task_status(
                    task, DataPullStatus.FAILED, error_message=str(e)
                )
            raise

        result = {"stats": stats, "request_logs": self.request_logs}
        return result

    def pull_order_detail(self, platform_order_id: str) -> Optional[Dict[str, Any]]:
        """
        拉取单个订单详情

        Args:
            platform_order_id: 平台订单ID

        Returns:
            订单详情数据
        """
        return self._get_single_trade_detail(platform_order_id)

    @transaction.atomic
    def save_order(self, order_data: Dict[str, Any]) -> bool:
        """
        保存订单数据到数据库

        Args:
            order_data: 订单数据

        Returns:
            是否为新订单
        """
        base_info = order_data.get("baseInfo", {})
        platform_order_id = str(base_info.get("id"))

        is_new = False

        try:
            order, created = Order.objects.get_or_create(
                store=self.store,
                platform_order_id=platform_order_id,
                defaults={
                    "platform_order_no": base_info.get("idOfStr"),
                    "order_status": base_info.get("status"),
                    "refund_status": base_info.get(
                        "refundStatus", RefundStatus.NO_REFUND
                    ),
                    "buyer_login_id": base_info.get("buyerLoginId"),
                    "buyer_open_uid": base_info.get("buyerOpenUid"),
                    "total_amount": base_info.get("totalAmount", 0),
                    "sum_product_payment": base_info.get("sumProductPayment", 0),
                    "shipping_fee": base_info.get("shippingFee", 0),
                    "discount": base_info.get("discount", 0),
                    "refund_amount": base_info.get("refund", 0),
                    "create_time": (
                        self._de_format_time(base_info.get("createTime"))
                        if base_info.get("createTime")
                        else None
                    ),
                    "pay_time": (
                        self._de_format_time(base_info.get("payTime"))
                        if base_info.get("payTime")
                        else None
                    ),
                    "modify_time": (
                        self._de_format_time(base_info.get("modifyTime"))
                        if base_info.get("modifyTime")
                        else None
                    ),
                    "seller_remark_icon": base_info.get("sellerRemarkIcon"),
                    "alipay_trade_id": base_info.get("alipayTradeId"),
                    "trade_type": base_info.get("tradeType"),
                    "flow_template_code": base_info.get("flowTemplateCode"),
                    "business_type": base_info.get("businessType"),
                    "platform_raw_data": order_data,
                },
            )

            is_new = created

            if not created:
                order.platform_order_no = base_info.get("idOfStr")
                order.order_status = base_info.get("status")
                order.refund_status = base_info.get(
                    "refundStatus", RefundStatus.NO_REFUND
                )
                order.total_amount = base_info.get("totalAmount", 0)
                order.sum_product_payment = base_info.get("sumProductPayment", 0)
                order.shipping_fee = base_info.get("shippingFee", 0)
                order.discount = base_info.get("discount", 0)
                order.refund_amount = base_info.get("refund", 0)
                order.modify_time = (
                    self._de_format_time(base_info.get("modifyTime"))
                    if base_info.get("modifyTime")
                    else None
                )
                order.platform_raw_data = order_data
                order.save()

            self._save_order_items(order, order_data.get("productItems", []))
            self._save_order_receiver(order, order_data)

            return is_new

        except Exception as e:
            raise Exception(f"保存订单失败: {str(e)}")

    def _save_order_items(self, order: Order, product_items: List[Dict[str, Any]]):
        """
        保存订单商品

        Args:
            order: 订单对象
            product_items: 商品列表
        """
        existing_item_ids = set(order.items.values_list("platform_item_id", flat=True))

        for item_data in product_items:
            platform_item_id = str(item_data.get("subItemID"))

            item, created = OrderItem.objects.get_or_create(
                order=order,
                platform_item_id=platform_item_id,
                defaults={
                    "product_id": (
                        str(item_data.get("productID"))
                        if item_data.get("productID")
                        else None
                    ),
                    "product_name": item_data.get("name", ""),
                    "product_img_url": (
                        ",".join(item_data.get("productImgUrl", []))
                        if item_data.get("productImgUrl")
                        else None
                    ),
                    "product_snapshot_url": item_data.get("productSnapshotUrl"),
                    "product_cargo_number": item_data.get("productCargoNumber")
                    or item_data.get("cargoNumber"),
                    "sku_id": (
                        str(item_data.get("skuID")) if item_data.get("skuID") else None
                    ),
                    "sku_specs": item_data.get("skuInfos", []),
                    "quantity": item_data.get("quantity", 0),
                    "price": item_data.get("price", 0),
                    "item_amount": item_data.get("itemAmount", 0),
                    "entry_discount": item_data.get("entryDiscount", 0),
                    "unit": item_data.get("unit"),
                    "item_status": item_data.get("status"),
                    "item_refund_status": item_data.get(
                        "refundStatus", RefundStatus.NO_REFUND
                    ),
                    "refund_id": item_data.get("refundId"),
                    "guarantees_terms": item_data.get("guaranteesTerms", []),
                    "logistics_status": item_data.get("logisticsStatus"),
                    "gmt_create": (
                        self._de_format_time(item_data.get("gmtCreate"))
                        if item_data.get("gmtCreate")
                        else None
                    ),
                    "gmt_modified": (
                        self._de_format_time(item_data.get("gmtModified"))
                        if item_data.get("gmtModified")
                        else None
                    ),
                    "platform_raw_data": item_data,
                },
            )

            if platform_item_id in existing_item_ids:
                existing_item_ids.remove(platform_item_id)

            if not created:
                item.product_name = item_data.get("name", "")
                item.item_status = item_data.get("status")
                item.item_refund_status = item_data.get(
                    "refundStatus", RefundStatus.NO_REFUND
                )
                item.item_amount = item_data.get("itemAmount", 0)
                item.gmt_modified = (
                    self._de_format_time(item_data.get("gmtModified"))
                    if item_data.get("gmtModified")
                    else None
                )
                item.platform_raw_data = item_data
                item.save()

        if existing_item_ids:
            OrderItem.objects.filter(
                order=order, platform_item_id__in=existing_item_ids
            ).delete()

    def _save_order_receiver(self, order: Order, order_data: Dict[str, Any]):
        """
        保存订单收货人信息

        Args:
            order: 订单对象
            order_data: 订单数据
        """
        base_info = order_data.get("baseInfo", {})

        receiver_info = base_info.get("receiveAddressInfo", {})

        if not receiver_info:
            return

        receiver, created = OrderReceiver.objects.get_or_create(
            order=order,
            defaults={
                "receiver_name": receiver_info.get("fullName"),
                "receiver_phone": receiver_info.get("phone"),
                "receiver_mobile": receiver_info.get("mobile"),
                "province": receiver_info.get("province"),
                "city": receiver_info.get("city"),
                "district": receiver_info.get("area"),
                "address": receiver_info.get("address"),
                "zip_code": receiver_info.get("zip"),
                "to_division_code": receiver_info.get("toDivisionCode"),
                "full_address": receiver_info.get("address"),
            },
        )

        if not created:
            receiver.receiver_name = receiver_info.get("fullName")
            receiver.receiver_phone = receiver_info.get("phone")
            receiver.receiver_mobile = receiver_info.get("mobile")
            receiver.province = receiver_info.get("province")
            receiver.city = receiver_info.get("city")
            receiver.district = receiver_info.get("area")
            receiver.address = receiver_info.get("address")
            receiver.full_address = receiver_info.get("address")
            receiver.save()
