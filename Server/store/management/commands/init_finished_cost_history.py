from django.core.management.base import BaseCommand
from django.db import transaction

from store.models import FinishedProduct
from store.views.helpers import record_finished_cost_history


class Command(BaseCommand):
    help = '为现有手串成品初始化成本历史快照（仅对尚无快照或成本已变化的成品记录）'

    def handle(self, *args, **options):
        created = 0
        skipped = 0

        for finished in FinishedProduct.objects.select_related('product').all():
            before = finished.cost_history.count()
            with transaction.atomic():
                record_finished_cost_history(finished, '初始化快照')
            after = finished.cost_history.count()
            if after > before:
                created += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f'初始化完成：新增快照 {created} 个，跳过 {skipped} 个（成本无变化）'
        ))
