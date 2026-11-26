import io
import json
import tempfile
import time
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import jwt
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import OperationalError
from django.test import TransactionTestCase, override_settings
from django.utils import timezone

from account.models import User, UserType
from company.models import Company
from store.models import Product, ProductType, Store, StoreDataConfig, DataPullTask, DataPullStatus
from store.tasks import auto_pull_orders


def png():
    buffer = io.BytesIO()
    Image.new('RGB', (4, 4), 'blue').save(buffer, format='PNG')
    return SimpleUploadedFile('image.png', buffer.getvalue(), 'image/png')


@override_settings(SECURE_SSL_REDIRECT=False, MEDIA_PROBE_FILE='', MEDIA_REQUIRE_MOUNT=False, WRITE_LOCK_FILE='')
class DeploymentTests(TransactionTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.media_settings = override_settings(MEDIA_ROOT=self.temp.name)
        self.media_settings.enable()
        self.addCleanup(self.media_settings.disable)
        self.company = Company.objects.create(name='Deployment fixture', code='deploy-a')
        self.other = Company.objects.create(name='Other company', code='deploy-b')
        self.user = User.objects.create_user(username='deploy-check', password='only-a-test', company=self.company, user_type=UserType.ENTERPRISE_LEADER)
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + jwt.encode({'user_id': self.user.pk}, settings.SECRET_KEY, algorithm='HS256')
        self.product = Product.objects.create(code='test-image', name='Image fixture', product_type=ProductType.ACCESSORY, company=self.company, selling_price=1, image=png())

    def update(self, **data):
        return self.client.post('/api/store/products/%s/update/' % self.product.pk, data)

    def test_image_replacement_deletes_old_only_after_commit(self):
        old = self.product.image.path
        response = self.update(image=png())
        self.assertEqual(response.status_code, 200, response.content)
        self.product.refresh_from_db()
        self.assertFalse(Path(old).exists())
        self.assertTrue(Path(self.product.image.path).exists())

    def test_failed_update_keeps_original_reference_and_file(self):
        old = self.product.image.name
        with patch.object(Product, 'save', side_effect=RuntimeError('simulated DB write failure')):
            response = self.update(image=png())
        self.assertEqual(response.status_code, 500)
        self.product.refresh_from_db()
        self.assertEqual(self.product.image.name, old)
        self.assertTrue(Path(self.product.image.path).exists())

    def test_failed_transaction_removes_new_image(self):
        from utils.media import product_mutation
        from django.http import JsonResponse
        old = self.product.image.name
        @product_mutation
        def fail_after_save(request):
            self.product.image = png()
            self.product.save()
            return JsonResponse({'error': 'failed after image write'}, status=400)
        fail_after_save(None)
        self.product.refresh_from_db()
        self.assertEqual(self.product.image.name, old)
        self.assertEqual(len(list(Path(self.temp.name).rglob('*.png'))), 1)

    def test_invalid_image_cannot_replace_valid_image(self):
        old = self.product.image.name
        response = self.update(image=SimpleUploadedFile('evil.jpg', b'<script>alert(1)</script>', 'image/jpeg'))
        self.assertEqual(response.status_code, 400, response.content)
        self.product.refresh_from_db()
        self.assertEqual(self.product.image.name, old)

    @override_settings(MEDIA_REQUIRE_MOUNT=True)
    def test_unmounted_media_rejects_upload(self):
        response = self.update(image=png())
        self.assertEqual(response.status_code, 503, response.content)
        self.assertEqual(len(list(Path(self.temp.name).rglob('*.png'))), 1)

    def test_other_company_cannot_edit_image(self):
        self.product.company = self.other
        self.product.save()
        response = self.update(image=png())
        self.assertEqual(response.status_code, 403)

    def test_company_cannot_create_in_other_company(self):
        response = self.client.post('/api/store/products/create/', {'code': 'cross-company', 'name': 'cross-company', 'product_type': 'accessory', 'company_id': self.other.pk, 'selling_price': '1'})
        self.assertEqual(response.status_code, 403, response.content)

    def test_database_outage_returns_503(self):
        with patch('wewin.middleware.connection.cursor', side_effect=OperationalError('offline')):
            response = self.client.get('/api/store/products/')
        self.assertEqual(response.status_code, 503)
        self.assertNotIn(b'offline', response.content)

    def test_backup_barrier_returns_503(self):
        with patch('wewin.middleware.write_lock', side_effect=BlockingIOError):
            response = self.client.get('/api/store/products/')
        self.assertEqual(response.status_code, 503)

    def test_old_snapshot_cannot_look_healthy_after_fresh_ack(self):
        status = Path(self.temp.name) / 'status.json'
        status.write_text(json.dumps({'completed_at': time.time(), 'source_created_at': time.time() - 1000}))
        with override_settings(BACKUP_STATUS_FILE=str(status), BACKUP_MAX_AGE_SECONDS=100):
            self.assertEqual(self.client.get('/health/backup/').status_code, 503)
        status.write_text(json.dumps({'completed_at': time.time(), 'source_created_at': time.time()}))
        with override_settings(BACKUP_STATUS_FILE=str(status), BACKUP_MAX_AGE_SECONDS=100):
            self.assertEqual(self.client.get('/health/backup/').status_code, 200)

    def test_failed_pull_keeps_recovery_start(self):
        store = Store.objects.create(name='Test store', platform='1688', company=self.company)
        config = StoreDataConfig.objects.create(store=store, auto_pull_enabled=True)
        watermark = timezone.now() - timedelta(days=2)
        DataPullTask.objects.create(store=store, task_type='auto_pull', status=DataPullStatus.SUCCESS, end_time=watermark)
        with patch('store.services.BaseDataPullService.get_service_class', side_effect=RuntimeError('unavailable')):
            auto_pull_orders()
        config.refresh_from_db()
        self.assertEqual(config.pull_status, DataPullStatus.FAILED)
        self.assertEqual(config.extra_config['recovery_start'], watermark.isoformat())
        self.assertEqual(DataPullTask.objects.filter(status=DataPullStatus.SUCCESS).latest('end_time').end_time, watermark)

    def test_successful_pull_starts_at_last_success(self):
        from store.services.base import BaseDataPullService
        store = Store.objects.create(name='Test store', platform='1688', company=self.company)
        StoreDataConfig.objects.create(store=store, auto_pull_enabled=True)
        watermark = timezone.now() - timedelta(days=2)
        DataPullTask.objects.create(store=store, task_type='auto_pull', status=DataPullStatus.SUCCESS, end_time=watermark)
        seen = []
        class Service:
            def __init__(self, store): self.store = store
            create_pull_task = BaseDataPullService.create_pull_task
            def pull_orders(self, start, end, task):
                seen.append(start)
                task.status = DataPullStatus.SUCCESS
                task.save()
                return {'stats': {'failed_count': 0}}
        with patch('store.services.BaseDataPullService.get_service_class', return_value=Service):
            auto_pull_orders()
        self.assertEqual(seen, [watermark])
        self.assertEqual(StoreDataConfig.objects.get(store=store).pull_status, DataPullStatus.SUCCESS)


    def test_text_edit_preserves_skus_used_by_finished_product(self):
        from store.models import Accessory, ProductSku, FinishedProduct, FinishedProductAccessory
        accessory = Accessory.objects.create(product=self.product)
        sku = ProductSku.objects.create(product=self.product, sku_code='material-sku', is_default=True)
        finished_product = Product.objects.create(code='finished-test', name='finished', product_type=ProductType.FINISHED, company=self.company, selling_price=10)
        finished = FinishedProduct.objects.create(product=finished_product)
        FinishedProductAccessory.objects.create(finished_product=finished, accessory=accessory, sku=sku, quantity=1)
        response = self.update(name='Updated text')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertTrue(ProductSku.objects.filter(pk=sku.pk).exists())

    def test_search_finds_older_product_before_paging_and_keeps_company_isolation(self):
        target = Product.objects.create(code='SEARCH-OLDER', name='Older target', product_type=ProductType.ACCESSORY,
                                        company=self.company, selling_price=1)
        Product.objects.bulk_create([Product(code=f'NEWER-{index}', name='Newer record', product_type=ProductType.ACCESSORY,
                                            company=self.company, selling_price=1) for index in range(55)])
        Product.objects.create(code='SEARCH-OTHER', name='Older target', product_type=ProductType.ACCESSORY,
                               company=self.other, selling_price=1)
        response = self.client.get('/api/store/products/', {'search': 'SEARCH', 'page_size': 50})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['total_count'], 1)
        self.assertEqual([row['id'] for row in response.json()['products']], [target.pk])
        by_name = self.client.get('/api/store/products/', {'search': 'Older target'})
        self.assertEqual([row['id'] for row in by_name.json()['products']], [target.pk])
