from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BasePlatformAdapter(ABC):
    """平台适配器基类，定义统一的接口"""

    @abstractmethod
    def __init__(self, store_config: Dict):
        """
        初始化平台适配器
        :param store_config: 店铺配置字典，包含API密钥等信息
        """
        pass

    @abstractmethod
    def fetch_order_list(self, start_time: str, end_time: str, page: int = 1, page_size: int = 20) -> Dict:
        """
        获取订单列表
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param page: 页码
        :param page_size: 每页数量
        :return: 订单列表数据
        """
        pass

    @abstractmethod
    def fetch_order_detail(self, order_id: str) -> Dict:
        """
        获取订单详情
        :param order_id: 平台订单ID
        :return: 订单详情数据
        """
        pass

    @abstractmethod
    def normalize_order_data(self, raw_order: Dict) -> Dict:
        """
        将原始订单数据标准化为统一格式
        :param raw_order: 原始订单数据
        :return: 标准化后的订单数据
        """
        pass
