import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from django.utils import timezone
from store.models import Store
from .adapter_factory import AdapterFactory
from .order_processor import OrderProcessor

logger = logging.getLogger(__name__)


class OrderPullService:
    """订单拉取服务，协调平台适配器、行业适配器和订单处理器"""

    def __init__(self, store: Store):
        self.store = store
        self.platform_adapter = None
        self.industry_adapter = None
        self.order_processor = OrderProcessor(store)

    def initialize_adapters(self, platform: str, industry: str, store_config: Dict):
        """
        初始化平台和行业适配器
        :param platform: 平台名称
        :param industry: 行业名称
        :param store_config: 店铺配置
        """
        self.platform_adapter = AdapterFactory.create_platform_adapter(platform, store_config)
        self.industry_adapter = AdapterFactory.create_industry_adapter(industry)

        if not self.platform_adapter:
            raise ValueError(f"不支持的平台: {platform}")

    def pull_orders(self, start_time: Optional[datetime] = None, 
                   end_time: Optional[datetime] = None,
                   days: int = 7) -> List[Dict]:
        """
        拉取订单数据
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param days: 默认拉取最近几天的数据
        :return: 处理的订单列表
        """
        if not self.platform_adapter:
            raise ValueError("请先初始化适配器")

        if not end_time:
            end_time = timezone.now()
        if not start_time:
            start_time = end_time - timedelta(days=days)

        formatted_start = self.platform_adapter.format_date(start_time)
        formatted_end = self.platform_adapter.format_date(end_time)

        logger.info(f"开始拉取订单: {self.store.name}, 时间范围: {formatted_start} - {formatted_end}")

        processed_orders = []
        page = 1
        page_size = 20

        while True:
            order_list_data = self.platform_adapter.fetch_order_list(
                formatted_start, formatted_end, page, page_size
            )

            if not order_list_data:
                logger.warning("获取订单列表失败")
                break

            result = order_list_data.get("result", [])
            if not result:
                break

            for raw_order in result:
                try:
                    order_id = str(raw_order.get("id", ""))
                    if not order_id:
                        continue

                    order_detail = self.platform_adapter.fetch_order_detail(order_id)
                    if not order_detail:
                        logger.warning(f"获取订单详情失败: {order_id}")
                        continue

                    normalized_data = self.platform_adapter.normalize_order_data(order_detail)

                    if self.industry_adapter:
                        if self.industry_adapter.should_filter_order(normalized_data):
                            logger.info(f"过滤订单: {order_id}")
                            continue
                        normalized_data = self.industry_adapter.process_order_data(normalized_data)

                    order = self.order_processor.process_order(normalized_data)
                    if order:
                        processed_orders.append({
                            "order_id": order.platform_order_id,
                            "status": order.status,
                            "total_amount": float(order.total_amount),
                        })
                        logger.info(f"处理订单成功: {order.platform_order_id}")

                except Exception as e:
                    logger.error(f"处理订单失败: {e}", exc_info=True)

            if len(result) < page_size:
                break

            page += 1

        logger.info(f"订单拉取完成，共处理 {len(processed_orders)} 个订单")
        return processed_orders
