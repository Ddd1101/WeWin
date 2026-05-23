from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..models import Store, DataPullTask, DataPullStatus


class BaseDataPullService(ABC):
    """
    数据拉取服务基类
    所有平台的数据拉取服务都需要继承此类
    """

    def __init__(self, store: Store):
        self.store = store
        self.api_config = None
        self._init_api_config()

    def _init_api_config(self):
        """初始化API配置"""
        if hasattr(self.store, 'api_config'):
            self.api_config = self.store.api_config

    @abstractmethod
    def pull_orders(self, start_time: datetime, end_time: datetime, 
                   task: Optional[DataPullTask] = None) -> Dict[str, Any]:
        """
        拉取订单数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            task: 数据拉取任务（可选）
            
        Returns:
            拉取结果统计信息
        """
        pass

    @abstractmethod
    def pull_order_detail(self, platform_order_id: str) -> Optional[Dict[str, Any]]:
        """
        拉取单个订单详情
        
        Args:
            platform_order_id: 平台订单ID
            
        Returns:
            订单详情数据
        """
        pass

    @abstractmethod
    def save_order(self, order_data: Dict[str, Any]) -> bool:
        """
        保存订单数据到数据库
        
        Args:
            order_data: 订单数据
            
        Returns:
            是否保存成功
        """
        pass

    def create_pull_task(self, task_type: str, start_time: datetime, 
                        end_time: datetime, params: Optional[Dict] = None) -> DataPullTask:
        """
        创建数据拉取任务
        
        Args:
            task_type: 任务类型
            start_time: 开始时间
            end_time: 结束时间
            params: 任务参数
            
        Returns:
            数据拉取任务
        """
        task = DataPullTask.objects.create(
            store=self.store,
            task_type=task_type,
            status=DataPullStatus.PENDING,
            start_time=start_time,
            end_time=end_time,
            params=params or {}
        )
        return task

    def update_task_status(self, task: DataPullTask, status: str, 
                          order_count: int = 0, new_order_count: int = 0,
                          updated_order_count: int = 0, error_message: Optional[str] = None):
        """
        更新任务状态
        
        Args:
            task: 数据拉取任务
            status: 状态
            order_count: 拉取订单数
            new_order_count: 新增订单数
            updated_order_count: 更新订单数
            error_message: 错误信息
        """
        task.status = status
        task.order_count = order_count
        task.new_order_count = new_order_count
        task.updated_order_count = updated_order_count
        if error_message:
            task.error_message = error_message
        task.save()

    def get_service_class(platform: str):
        """
        根据平台类型获取对应的服务类
        
        Args:
            platform: 平台类型
            
        Returns:
            服务类
        """
        from .ali1688 import Ali1688DataPullService
        
        service_map = {
            '1688': Ali1688DataPullService,
        }
        
        return service_map.get(platform)
