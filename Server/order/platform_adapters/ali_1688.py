import hmac
import requests
from datetime import datetime
from typing import Dict
from .base import BasePlatformAdapter


class Ali1688Adapter(BasePlatformAdapter):
    """1688平台适配器"""

    BASE_URL = "https://gw.open.1688.com/openapi/"
    REQUEST_TYPE_TRADE = "param2/1/com.alibaba.trade/"
    REQUEST_TYPE_DELIVERY = "param2/1/com.alibaba.logistics/"

    def __init__(self, store_config: Dict):
        """
        初始化1688平台适配器
        :param store_config: 店铺配置字典，包含app_key、app_secret、access_token等
        """
        self.app_key = store_config.get("app_key")
        self.app_secret = store_config.get("app_secret", "").encode("utf-8")
        self.access_token = store_config.get("access_token")
        self.shop_name = store_config.get("shop_name", "")

    def calculate_signature(self, url_path: str, data: Dict) -> str:
        """
        计算1688 API签名
        :param url_path: API路径
        :param data: 请求参数
        :return: 签名字符串
        """
        params = []
        for key in sorted(data.keys()):
            params.append(key + str(data[key]))
        assembled_params = "".join(params)
        merged_params = url_path + assembled_params
        merged_params = merged_params.encode("utf-8")
        
        hex_res = hmac.new(
            self.app_secret, merged_params, digestmod="sha1"
        ).hexdigest()
        
        return hex_res.upper()

    def format_date(self, date: datetime) -> str:
        """
        格式化日期为1688 API所需格式
        :param date: 日期对象
        :return: 格式化后的日期字符串
        """
        return date.strftime("%Y%m%d") + "000000000+0800"

    def fetch_order_list(self, start_time: str, end_time: str, page: int = 1, page_size: int = 20) -> Dict:
        """
        获取订单列表
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param page: 页码
        :param page_size: 每页数量
        :return: 订单列表数据
        """
        api_path = self.REQUEST_TYPE_TRADE + "alibaba.trade.getSellerOrderList/" + self.app_key
        full_url = self.BASE_URL + api_path
        
        data = {
            "access_token": self.access_token,
            "page": page,
            "pageSize": page_size,
            "createStartTime": start_time,
            "createEndTime": end_time,
        }
        
        signature = self.calculate_signature(api_path, data)
        data["_aop_signature"] = signature
        
        try:
            res = requests.post(full_url, data=data)
            return res.json()
        except Exception as e:
            print(f"获取订单列表失败: {e}")
            return {}

    def fetch_order_detail(self, order_id: str) -> Dict:
        """
        获取订单详情
        :param order_id: 平台订单ID
        :return: 订单详情数据
        """
        api_path = self.REQUEST_TYPE_TRADE + "alibaba.trade.get.sellerView/" + self.app_key
        full_url = self.BASE_URL + api_path
        
        data = {
            "access_token": self.access_token,
            "orderId": order_id,
        }
        
        signature = self.calculate_signature(api_path, data)
        data["_aop_signature"] = signature
        
        try:
            res = requests.post(full_url, data=data)
            return res.json()
        except Exception as e:
            print(f"获取订单详情失败: {e}")
            return {}

    def fetch_logistics_info(self, order_id: str) -> Dict:
        """
        获取物流信息
        :param order_id: 平台订单ID
        :return: 物流信息数据
        """
        api_path = self.REQUEST_TYPE_DELIVERY + "alibaba.trade.getLogisticsInfos.sellerView/" + self.app_key
        full_url = self.BASE_URL + api_path
        
        data = {
            "access_token": self.access_token,
            "orderId": order_id,
        }
        
        signature = self.calculate_signature(api_path, data)
        data["_aop_signature"] = signature
        
        try:
            res = requests.post(full_url, data=data)
            return res.json()
        except Exception as e:
            print(f"获取物流信息失败: {e}")
            return {}

    def normalize_order_data(self, raw_order: Dict) -> Dict:
        """
        将原始订单数据标准化为统一格式
        :param raw_order: 原始订单数据
        :return: 标准化后的订单数据
        """
        order_info = raw_order.get("result", {}).get("toReturn", {}).get("orderInfo", {})
        
        normalized = {
            "platform_order_id": str(order_info.get("id", "")),
            "status": order_info.get("status", ""),
            "total_amount": order_info.get("totalAmount", 0),
            "payment": order_info.get("payment", 0),
            "discount": order_info.get("discount", 0),
            "post_fee": order_info.get("postFee", 0),
            "buyer_member_id": order_info.get("buyerMemberId", ""),
            "buyer_login_id": order_info.get("buyerLoginId", ""),
            "buyer_contact": order_info.get("buyerContact", {}),
            "receive_address": order_info.get("receiveAddress", {}),
            "order_items": [],
            "gmt_create": order_info.get("gmtCreate", ""),
            "gmt_payment": order_info.get("gmtPayTime", ""),
            "gmt_modified": order_info.get("gmtModified", ""),
            "gmt_trade_success": order_info.get("gmtTradeSuccess", ""),
            "refund": order_info.get("refund", {}),
            "step_order_info": order_info.get("stepOrderInfo", {}),
            "raw_data": raw_order,
        }
        
        order_items = raw_order.get("result", {}).get("toReturn", {}).get("orderItems", [])
        for item in order_items:
            normalized["order_items"].append({
                "item_id": str(item.get("cargoNumber", "")),
                "sku_id": str(item.get("skuId", "")),
                "product_name": item.get("productName", ""),
                "product_img_url": item.get("productImgUrl", ""),
                "quantity": item.get("quantity", 0),
                "price": item.get("price", 0),
                "item_amount": item.get("itemAmount", 0),
                "spec_id": item.get("specId", ""),
                "spec_info": item.get("specInfo", ""),
                "description": item.get("description", ""),
                "raw_data": item,
            })
        
        return normalized
