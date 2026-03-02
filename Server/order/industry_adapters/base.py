from abc import ABC, abstractmethod
from typing import Dict


class BaseIndustryAdapter(ABC):
    """行业适配器基类，处理同平台不同行业的数据差异"""

    @abstractmethod
    def process_order_data(self, normalized_data: Dict) -> Dict:
        """
        处理行业特定的订单数据
        :param normalized_data: 标准化后的订单数据
        :return: 处理后的订单数据
        """
        pass

    @abstractmethod
    def should_filter_order(self, order_data: Dict) -> bool:
        """
        判断是否需要过滤该订单（如刷单等）
        :param order_data: 订单数据
        :return: 是否过滤
        """
        pass
