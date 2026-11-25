import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from django.db import connection
from django.test import override_settings, TransactionTestCase
from django.core.files.storage import storages
from store.test_deployment import png
from store.models import Product


@override_settings(MEDIA_ORIGIN_URL='http://127.0.0.1:10080', MEDIA_ORIGIN_READ_TOKEN='r'*40,
                   MEDIA_ORIGIN_WRITE_TOKEN='w'*40,
                   STORAGES={'default': {'BACKEND': 'utils.remote_media.N1ImageStorage'},
                             'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class RemoteMediaTests(TransactionTestCase):
    # Only these tests run here; the original local-storage tests run separately.
    def setUp(self):
        from django.test import TransactionTestCase
        from company.models import Company
        from account.models import User, UserType
        import jwt
        from django.conf import settings
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.config = override_settings(MEDIA_CLEANUP_DIR=self.temp.name, MEDIA_CACHE_ROOT='', WRITE_LOCK_FILE='')
        self.config.enable()
        self.addCleanup(self.config.disable)
        self.company = Company.objects.create(name='Remote test', code='remote-a')
        self.other = Company.objects.create(name='Other', code='remote-b')
        self.user = User.objects.create_user(username='remote', password='test-only', company=self.company, user_type=UserType.ENTERPRISE_LEADER)
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + jwt.encode({'user_id': self.user.pk}, settings.SECRET_KEY, algorithm='HS256')
        self.product = Product.objects.create(code='remote-image', name='remote', product_type='accessory', company=self.company, selling_price=1, image='products/original.png')

    def update(self, **data):
        return self.client.post('/api/store/products/%s/update/' % self.product.pk, data)

    def test_remote_upload_precedes_transaction(self):
        def save(name, upload):
            self.assertFalse(connection.in_atomic_block)
            return name
        with override_settings(SECURE_SSL_REDIRECT=False), patch('utils.media.default_storage.save', side_effect=save):
            response = self.update(image=png())
        self.assertEqual(response.status_code, 200, response.content)
        self.product.refresh_from_db()
        self.assertNotEqual(self.product.image.name, 'products/original.png')
        records = [json.loads(p.read_text()) for p in Path(self.temp.name).glob('*.json')]
        self.assertEqual(records[0]['name'], 'products/original.png')

    def test_shared_reference_is_never_deleted(self):
        from utils.media import queue_cleanup
        from django.core.management import call_command
        queue_cleanup(self.product.image.name, 'obsolete')
        with patch('utils.remote_media.remote_request') as remote:
            call_command('cleanup_media')
        remote.assert_not_called()
        self.assertEqual(list(Path(self.temp.name).glob('*.json')), [])

    def test_origin_failure_keeps_old_reference(self):
        from utils.media import StorageUnavailable
        with override_settings(SECURE_SSL_REDIRECT=False), patch('utils.media.default_storage.save', side_effect=StorageUnavailable('down')):
            response = self.update(image=png())
        self.assertEqual(response.status_code, 503)
        self.product.refresh_from_db()
        self.assertEqual(self.product.image.name, 'products/original.png')

    def test_cross_company_upload_rejected_before_network(self):
        self.product.company = self.other
        self.product.save()
        with override_settings(SECURE_SSL_REDIRECT=False), patch('utils.media.default_storage.save') as remote:
            response = self.update(image=png())
        self.assertEqual(response.status_code, 403)
        remote.assert_not_called()

