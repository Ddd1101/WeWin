import json
from decimal import Decimal
from unittest.mock import patch

import jwt
from django.conf import settings
from django.test import TestCase, override_settings

from account.models import User, UserType
from company.models import Company
from store.models import Product, ProductType, Accessory, FinishedProduct, FinishedProductAccessory
from store.views.helpers import record_finished_cost_history


@override_settings(SECURE_SSL_REDIRECT=False, WRITE_LOCK_FILE='')
class FinishedCostModeTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Cost modes', code='cost-modes')
        self.user = User.objects.create_user(username='cost-leader', company=self.company, user_type=UserType.ENTERPRISE_LEADER)
        self.client.defaults['HTTP_AUTHORIZATION'] = 'Bearer ' + jwt.encode({'user_id': self.user.pk}, settings.SECRET_KEY, algorithm='HS256')
        self.material = Product.objects.create(code='material', name='Material', product_type=ProductType.ACCESSORY, company=self.company, cost_price=50, selling_price=100)
        self.accessory = Accessory.objects.create(product=self.material)
        self.auto = self.finished('auto', 'auto')
        self.manual = self.finished('manual', 'manual')

    def finished(self, code, mode):
        product = Product.objects.create(code=code, name=code, product_type=ProductType.FINISHED, company=self.company, selling_price=100)
        finished = FinishedProduct.objects.create(product=product, cost_mode=mode, manual_cost=48, labor_cost=5)
        FinishedProductAccessory.objects.create(finished_product=finished, accessory=self.accessory, quantity=1)
        record_finished_cost_history(finished, 'fixture', self.user, 'creation')
        return finished

    def update(self, product, **data):
        return self.client.post(f'/api/store/products/{product.pk}/update/', json.dumps(data), content_type='application/json')

    def detail(self, finished):
        response = self.client.get(f'/api/store/products/{finished.pk}/detail/')
        self.assertEqual(response.status_code, 200, response.content)
        return response.json()

    def test_material_change_updates_only_auto_adopted_cost_and_preserves_snapshots(self):
        before = list(self.manual.cost_history.values())
        response = self.update(self.material, cost_price=57)
        self.assertEqual(response.status_code, 200, response.content)
        self.auto.product.refresh_from_db()
        self.manual.product.refresh_from_db()
        self.assertEqual(self.auto.product.cost_price, Decimal('62'))
        self.assertEqual(self.manual.product.cost_price, Decimal('48'))
        latest = self.manual.cost_history.latest('id')
        self.assertEqual(latest.reference_cost, Decimal('62'))
        self.assertEqual(latest.change_type, 'material_change')
        self.assertEqual(list(self.manual.cost_history.filter(pk=before[0]['id']).values()), before)
        detail = self.detail(self.manual)
        self.assertEqual(detail['cost_price'], 48)
        self.assertEqual(detail['finished']['reference_cost'], 62)
        listing = self.client.get('/api/store/products/?product_type=finished').json()['products']
        self.assertEqual(next(p for p in listing if p['id'] == self.manual.pk)['cost_price'], 48)

    def test_old_client_and_metadata_edits_cannot_overwrite_manual_cost(self):
        count = self.manual.cost_history.count()
        response = self.update(self.manual.product, name='Renamed', cost_price=999)
        self.assertEqual(response.status_code, 200, response.content)
        self.manual.product.refresh_from_db()
        self.assertEqual(self.manual.product.cost_price, Decimal('48'))
        self.assertEqual(self.manual.cost_history.count(), count)

    def test_manual_adjustment_and_equal_amount_mode_switch_are_recorded(self):
        response = self.update(self.manual.product, manual_cost='50.00', cost_note='供应商协议变更')
        self.assertEqual(response.status_code, 200, response.content)
        latest = self.manual.cost_history.latest('id')
        self.assertEqual(latest.cost_price, Decimal('50'))
        self.assertEqual(latest.reference_cost, Decimal('55'))
        self.assertEqual(latest.created_by, self.user)
        response = self.update(self.auto.product, cost_mode='manual', manual_cost=55, cost_note='锁定协议成本')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.auto.cost_history.latest('id').change_type, 'mode_switch')
        response = self.update(self.auto.product, cost_mode='auto', cost_note='改为自行组装')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.auto.cost_history.count(), 3)

    def test_invalid_cost_and_missing_reason_reject_without_mutation(self):
        for data in ({'manual_cost': -1}, {'manual_cost': 'NaN'}, {'manual_cost': 'Infinity'}, {'manual_cost': '1.001'}, {'manual_cost': 'no'}, {'manual_cost': 49}, {'cost_mode': 'invalid'}, {'cost_mode': 'auto'}, {'cost_note': 'x' * 401}):
            with self.subTest(data=data):
                response = self.update(self.manual.product, name='Must not persist', **data)
                self.assertEqual(response.status_code, 400, response.content)
                self.manual.product.refresh_from_db()
                self.assertEqual(self.manual.product.name, 'manual')
        self.assertEqual(self.manual.cost_history.count(), 1)

    def test_manual_create_requires_explicit_cost_and_reason(self):
        base = {'code': 'new', 'name': 'new', 'product_type': 'finished', 'cost_mode': 'manual'}
        for extra in ({}, {'manual_cost': 48}):
            response = self.client.post('/api/store/products/create/', json.dumps({**base, **extra}), content_type='application/json')
            self.assertEqual(response.status_code, 400, response.content)
            self.assertFalse(Product.objects.filter(code='new').exists())
        response = self.client.post('/api/store/products/create/', json.dumps({**base, 'manual_cost': 0, 'cost_note': '免费样品'}), content_type='application/json')
        self.assertEqual(response.status_code, 201, response.content)
        created = FinishedProduct.objects.get(product__code='new')
        self.assertEqual(created.cost_mode, 'manual')
        self.assertEqual(created.product.cost_price, 0)

    def test_composition_changes_only_reference_for_manual(self):
        response = self.update(self.manual.product, accessories=[{'accessory_id': self.material.pk, 'quantity': 2}], labor_cost=7)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(self.detail(self.manual)['finished']['reference_cost'], 107)
        self.assertEqual(self.detail(self.manual)['cost_price'], 48)

    def test_failure_in_related_recalculation_rolls_back_material_and_all_history(self):
        with patch('store.views.helpers.record_finished_cost_history', side_effect=RuntimeError('cost failure')):
            response = self.update(self.material, cost_price=57)
        self.assertEqual(response.status_code, 500)
        self.material.refresh_from_db()
        self.assertEqual(self.material.cost_price, Decimal('50'))
        self.assertEqual(self.auto.cost_history.count(), 1)
        self.assertEqual(self.manual.cost_history.count(), 1)

    def test_other_enterprise_cannot_adjust_or_view_history(self):
        other = Company.objects.create(name='Other', code='cost-other')
        self.user.company = other
        self.user.save()
        self.assertEqual(self.update(self.manual.product, manual_cost=49, cost_note='No access').status_code, 403)
        self.assertEqual(self.client.get(f'/api/store/products/{self.manual.pk}/cost-history/').status_code, 403)
