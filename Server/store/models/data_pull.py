from django.db import models
from .store import Store


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
        return f'{self.store.name} - {self.task_type} - {self.get_status_display()}'


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
