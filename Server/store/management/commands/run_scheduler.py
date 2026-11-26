import fcntl
import signal
from pathlib import Path
from apscheduler.schedulers.blocking import BlockingScheduler
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import close_old_connections
from store.tasks import auto_pull_orders
from utils.write_lock import write_lock


class Command(BaseCommand):
    help = 'Run the single automatic order-pull scheduler (separate from web workers).'

    def handle(self, *args, **options):
        Path(settings.SCHEDULER_LOCK_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(settings.SCHEDULER_LOCK_FILE, 'a') as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise CommandError('Another scheduler already holds the lock') from exc
            scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)

            def pull():
                close_old_connections()
                try:
                    with write_lock():
                        auto_pull_orders()
                except BlockingIOError:
                    self.stdout.write('Backup in progress; retry on next tick')
                finally:
                    close_old_connections()

            scheduler.add_job(pull, 'interval', minutes=1, max_instances=1, coalesce=True)
            signal.signal(signal.SIGTERM, lambda *_: scheduler.shutdown(wait=True))
            self.stdout.write('Single order scheduler started')
            try:
                scheduler.start()
            except KeyboardInterrupt:
                scheduler.shutdown(wait=True)
