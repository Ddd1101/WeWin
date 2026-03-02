from typing import Dict
from .base import BaseIndustryAdapter


class CrystalBraceletAdapter(BaseIndustryAdapter):
    """水晶手串行业适配器"""

    # 订单标签类型
    ORDER_TAG_RED = "1"
    ORDER_TAG_BLUE = "2"
    ORDER_TAG_GREEN = "3"
    ORDER_TAG_YELLOW = "4"

    def process_order_data(self, normalized_data: Dict) -> Dict:
        """
        处理水晶手串行业特定的订单数据
        :param normalized_data: 标准化后的订单数据
        :return: 处理后的订单数据
        """
        return normalized_data

    def should_filter_order(self, order_data: Dict) -> bool:
        """
        判断是否需要过滤该订单（过滤刷单等）
        :param order_data: 订单数据
        :return: 是否过滤
        """
        raw_data = order_data.get("raw_data", {})
        base_info = raw_data.get("result", {}).get("toReturn", {}).get("orderInfo", {})
        seller_remark_icon = base_info.get("sellerRemarkIcon", "")

        if seller_remark_icon in [self.ORDER_TAG_BLUE, self.ORDER_TAG_GREEN]:
            return True

        return False
