from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

from django.utils import timezone


def auto_pull_orders():
    """
    定时自动拉单任务：遍历启用了自动拉取的店铺，按拉取间隔触发拉取。
    由 apscheduler 周期性调用（见 management/commands/run_scheduler.py）。
    """
    from store.models import StoreDataConfig, DataPullStatus, DataPullTask
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
            end_time = now
            last_success = DataPullTask.objects.filter(
                store=store, task_type='auto_pull', status=DataPullStatus.SUCCESS,
                end_time__isnull=False,
            ).order_by('-end_time').first()
            start_time = min(last_success.end_time, now) if last_success else now - timedelta(hours=interval_hours)
            # Retain the start of the first failed interval until it succeeds.
            recovery_start = config.extra_config.get('recovery_start')
            if recovery_start:
                from django.utils.dateparse import parse_datetime
                parsed = parse_datetime(recovery_start)
                if parsed:
                    start_time = min(start_time, parsed)
            config.extra_config['recovery_start'] = start_time.isoformat()
            config.save(update_fields=['extra_config'])

            service_class = BaseDataPullService.get_service_class(store.platform)
            if not service_class:
                raise RuntimeError('Platform does not support automatic order pulling')
            service = service_class(store)

            task = service.create_pull_task(
                'auto_pull', start_time, end_time, {'source': 'auto'}
            )
            result = service.pull_orders(start_time, end_time, task)
            task.refresh_from_db()
            if task.status != DataPullStatus.SUCCESS or result.get('error') or result.get('stats', {}).get('failed_count', 0):
                task.status = DataPullStatus.FAILED
                task.save(update_fields=['status'])
                raise RuntimeError('Order pull did not complete successfully')
            config.extra_config.pop('recovery_start', None)
            config.pull_status = DataPullStatus.SUCCESS
        except Exception as e:
            config.pull_status = DataPullStatus.FAILED
            logger.exception('Automatic pull failed for store %s', store.pk)
        finally:
            config.last_pull_time = now
            config.next_pull_time = now + timedelta(hours=interval_hours)
            config.save()
