import logging
from django.core.management.base import BaseCommand, CommandError
from store.models import Store
from order.services.order_pull_service import OrderPullService
from order.services.adapter_factory import AdapterFactory

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = '从电商平台拉取订单数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--store-id',
            type=int,
            help='指定店铺ID，如果不指定则拉取所有启用的1688店铺',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='拉取最近几天的订单，默认为7天',
        )

    def handle(self, *args, **options):
        store_id = options.get('store_id')
        days = options.get('days')

        if store_id:
            try:
                store = Store.objects.get(id=store_id, is_active=True)
                self.pull_orders_for_store(store, days)
            except Store.DoesNotExist:
                raise CommandError(f'店铺ID {store_id} 不存在或未启用')
        else:
            stores = Store.objects.filter(
                is_active=True,
                platform__in=['1688']
            )
            if not stores:
                self.stdout.write(self.style.WARNING('没有找到启用的1688店铺'))
                return

            for store in stores:
                self.pull_orders_for_store(store, days)

    def pull_orders_for_store(self, store: Store, days: int):
        self.stdout.write(self.style.NOTICE(f'开始处理店铺: {store.name}'))

        try:
            platform_map = {
                '1688': AdapterFactory.PLATFORM_ALI_1688,
            }
            category_map = {
                'crystal_bracelet': AdapterFactory.INDUSTRY_CRYSTAL_BRACELET,
            }

            platform = platform_map.get(store.platform)
            industry = category_map.get(store.category)

            if not platform:
                self.stdout.write(self.style.WARNING(f'不支持的平台: {store.platform}'))
                return

            store_config = store.api_config.copy()
            store_config['shop_name'] = store.name

            service = OrderPullService(store)
            service.initialize_adapters(platform, industry, store_config)

            processed_orders = service.pull_orders(days=days)

            self.stdout.write(
                self.style.SUCCESS(
                    f'店铺 {store.name} 处理完成，共处理 {len(processed_orders)} 个订单'
                )
            )

        except Exception as e:
            logger.error(f'处理店铺 {store.name} 失败: {e}', exc_info=True)
            self.stdout.write(
                self.style.ERROR(f'处理店铺 {store.name} 失败: {e}')
            )
