import os

from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    verbose_name = '店铺管理'

    def ready(self):
        self._start_scheduler()

    def _start_scheduler(self):
        # 仅 runserver 的 reload 子进程启动，避免 watchdog 主进程重复启动；
        # 生产环境（gunicorn 等）无 RUN_MAIN，也会正常启动一次。
        if os.environ.get('RUN_MAIN') is not None and os.environ.get('RUN_MAIN') != 'true':
            return

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger

            from store.tasks import auto_pull_orders

            scheduler = BackgroundScheduler()
            scheduler.add_job(
                auto_pull_orders,
                trigger=IntervalTrigger(minutes=1),
                id='auto_pull_orders',
                replace_existing=True,
            )
            scheduler.start()
        except Exception as e:
            print(f'启动自动拉单调度器失败: {e}')
