from datetime import timedelta

from django.utils import timezone


def auto_pull_orders():
    """
    定时自动拉单任务：遍历启用了自动拉取的店铺，按拉取间隔触发拉取。
    由 apscheduler 周期性调用（见 store/apps.py）。
    """
    from store.models import StoreDataConfig, DataPullStatus
    from store.services import BaseDataPullService

    now = timezone.now()
    configs = StoreDataConfig.objects.filter(
        auto_pull_enabled=True,
        store__is_active=True,
    ).select_related('store')

    for config in configs:
        # 未到下次拉取时间则跳过
        if config.next_pull_time and config.next_pull_time > now:
            continue

        store = config.store
        interval_hours = config.pull_interval_hours or 1

        try:
            service_class = BaseDataPullService.get_service_class(store.platform)
            if not service_class:
                continue

            service = service_class(store)
            end_time = now
            start_time = now - timedelta(hours=interval_hours)

            task = service.create_pull_task(
                'auto_pull', start_time, end_time, {'source': 'auto'}
            )
            service.pull_orders(start_time, end_time, task)

            config.pull_status = DataPullStatus.SUCCESS
        except Exception as e:
            config.pull_status = DataPullStatus.FAILED
            print(f'自动拉单失败: {store.name} - {e}')
        finally:
            config.last_pull_time = now
            config.next_pull_time = now + timedelta(hours=interval_hours)
            config.save()
