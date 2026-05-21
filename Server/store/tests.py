from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from datetime import datetime, timedelta
import jwt
from account.models import User, UserType
from company.models import Company
from store.models import Product, ProductType, Bead, Accessory, FinishedProduct
import json


class ProductPermissionTests(TestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name='企业A', code='COMPA')
        self.company_b = Company.objects.create(name='企业B', code='COMPB')
        
        self.super_admin = User.objects.create_user(
            username='super_admin',
            password='test123',
            user_type=UserType.SUPER_ADMIN
        )
        
        self.site_admin = User.objects.create_user(
            username='site_admin',
            password='test123',
            user_type=UserType.SITE_ADMIN
        )
        
        self.enterprise_leader_a = User.objects.create_user(
            username='leader_a',
            password='test123',
            user_type=UserType.ENTERPRISE_LEADER,
            company=self.company_a
        )
        
        self.enterprise_admin_a = User.objects.create_user(
            username='admin_a',
            password='test123',
            user_type=UserType.ENTERPRISE_ADMIN,
            company=self.company_a
        )
        
        self.enterprise_user_a = User.objects.create_user(
            username='user_a',
            password='test123',
            user_type=UserType.ENTERPRISE_USER,
            company=self.company_a
        )
        
        self.temp_user_a = User.objects.create_user(
            username='temp_a',
            password='test123',
            user_type=UserType.TEMPORARY,
            company=self.company_a
        )
        
        self.enterprise_leader_b = User.objects.create_user(
            username='leader_b',
            password='test123',
            user_type=UserType.ENTERPRISE_LEADER,
            company=self.company_b
        )
        
        self.product_a = Product.objects.create(
            code='PROD_A',
            name='企业A商品',
            product_type=ProductType.BEAD,
            cost_price=10.0,
            selling_price=20.0,
            company=self.company_a,
            created_by=self.enterprise_leader_a
        )
        
        Bead.objects.create(
            product=self.product_a,
            material='玛瑙',
            size='8mm',
            color='红色',
            weight=2.5,
            quality_level=5
        )
        
        self.product_b = Product.objects.create(
            code='PROD_B',
            name='企业B商品',
            product_type=ProductType.ACCESSORY,
            cost_price=5.0,
            selling_price=10.0,
            company=self.company_b,
            created_by=self.enterprise_leader_b
        )
        
        Accessory.objects.create(
            product=self.product_b,
            material='金属',
            size='10mm',
            color='银色'
        )

    def get_token_for_user(self, user):
        payload = {
            'user_id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'exp': datetime.utcnow() + timedelta(days=7)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return {'HTTP_AUTHORIZATION': f'Bearer {token}'}

    def test_get_products_permissions(self):
        test_cases = [
            (self.super_admin, [self.product_a, self.product_b], 200, '超级管理员应能看到所有商品'),
            (self.site_admin, [self.product_a, self.product_b], 200, '网站管理员应能看到所有商品'),
            (self.enterprise_leader_a, [self.product_a], 200, '企业负责人应只能看到自己企业的商品'),
            (self.enterprise_admin_a, [self.product_a], 200, '企业管理员应只能看到自己企业的商品'),
            (self.enterprise_user_a, [self.product_a], 200, '企业用户应只能看到自己企业的商品'),
            (self.temp_user_a, [], 200, '临时用户不应能看到任何商品'),
            (self.enterprise_leader_b, [self.product_b], 200, '企业B负责人应只能看到企业B的商品'),
        ]

        for user, expected_products, expected_status, message in test_cases:
            with self.subTest(user=user.username, message=message):
                headers = self.get_token_for_user(user)
                response = self.client.get(reverse('get-products'), **headers)
                self.assertEqual(response.status_code, expected_status, f'{message}, 响应内容: {response.content}')
                if expected_status == 200:
                    products_data = json.loads(response.content)['products']
                    product_ids = [p['id'] for p in products_data]
                    expected_ids = [p.id for p in expected_products]
                    self.assertEqual(set(product_ids), set(expected_ids), message)

    def test_get_product_detail_permissions(self):
        test_cases = [
            (self.super_admin, self.product_a.id, 200, '超级管理员应能查看任何企业的商品详情'),
            (self.site_admin, self.product_a.id, 200, '网站管理员应能查看任何企业的商品详情'),
            (self.enterprise_leader_a, self.product_a.id, 200, '企业负责人应能查看自己企业的商品详情'),
            (self.enterprise_admin_a, self.product_a.id, 200, '企业管理员应能查看自己企业的商品详情'),
            (self.enterprise_user_a, self.product_a.id, 200, '企业用户应能查看自己企业的商品详情'),
            (self.temp_user_a, self.product_a.id, 403, '临时用户不应能查看任何商品详情'),
            (self.enterprise_leader_b, self.product_a.id, 403, '企业B负责人不应能查看企业A的商品详情'),
        ]

        for user, product_id, expected_status, message in test_cases:
            with self.subTest(user=user.username, message=message):
                headers = self.get_token_for_user(user)
                url = reverse('get-product-detail', args=[product_id])
                response = self.client.get(url, **headers)
                self.assertEqual(response.status_code, expected_status, message)

    def test_create_product_permissions(self):
        test_cases = [
            (self.super_admin, self.company_a, 201, '超级管理员应能创建商品'),
            (self.site_admin, self.company_a, 201, '网站管理员应能创建商品'),
            (self.enterprise_leader_a, self.company_a, 201, '企业负责人应能创建自己企业的商品'),
            (self.enterprise_admin_a, self.company_a, 201, '企业管理员应能创建自己企业的商品'),
            (self.enterprise_user_a, self.company_a, 403, '企业用户不应能创建商品'),
            (self.temp_user_a, self.company_a, 403, '临时用户不应能创建商品'),
        ]

        for user, company, expected_status, message in test_cases:
            with self.subTest(user=user.username, message=message):
                headers = self.get_token_for_user(user)
                data = {
                    'code': f'NEW_{user.username}',
                    'name': f'新商品_{user.username}',
                    'product_type': ProductType.BEAD,
                    'cost_price': 15.0,
                    'selling_price': 30.0,
                    'company_id': company.id,
                    'material': '水晶',
                    'size': '10mm',
                    'color': '蓝色',
                    'weight': 3.0
                }
                response = self.client.post(
                    reverse('create-product'),
                    data=json.dumps(data),
                    content_type='application/json',
                    **headers
                )
                self.assertEqual(response.status_code, expected_status, message)

    def test_update_product_permissions(self):
        test_cases = [
            (self.super_admin, self.product_a.id, 200, '超级管理员应能更新任何企业的商品'),
            (self.site_admin, self.product_a.id, 200, '网站管理员应能更新任何企业的商品'),
            (self.enterprise_leader_a, self.product_a.id, 200, '企业负责人应能更新自己企业的商品'),
            (self.enterprise_admin_a, self.product_a.id, 200, '企业管理员应能更新自己企业的商品'),
            (self.enterprise_user_a, self.product_a.id, 403, '企业用户不应能更新商品'),
            (self.temp_user_a, self.product_a.id, 403, '临时用户不应能更新商品'),
            (self.enterprise_leader_b, self.product_a.id, 403, '企业B负责人不应能更新企业A的商品'),
        ]

        for user, product_id, expected_status, message in test_cases:
            with self.subTest(user=user.username, message=message):
                headers = self.get_token_for_user(user)
                data = {'name': f'更新后的名称_{user.username}'}
                url = reverse('update-product', args=[product_id])
                response = self.client.put(
                    url,
                    data=json.dumps(data),
                    content_type='application/json',
                    **headers
                )
                self.assertEqual(response.status_code, expected_status, message)

    def test_delete_product_permissions(self):
        test_cases = [
            (self.super_admin, '超级管理员应能删除任何企业的商品'),
            (self.site_admin, '网站管理员应能删除任何企业的商品'),
            (self.enterprise_leader_a, '企业负责人应能删除自己企业的商品'),
            (self.enterprise_admin_a, '企业管理员应能删除自己企业的商品'),
        ]

        for user, message in test_cases:
            with self.subTest(user=user.username, message=message):
                product = Product.objects.create(
                    code=f'DEL_TEST_{user.username}',
                    name=f'删除测试商品_{user.username}',
                    product_type=ProductType.ACCESSORY,
                    cost_price=5.0,
                    selling_price=10.0,
                    company=self.company_a,
                    created_by=self.enterprise_leader_a
                )
                
                headers = self.get_token_for_user(user)
                url = reverse('delete-product', args=[product.id])
                response = self.client.delete(url, **headers)
                self.assertEqual(response.status_code, 200, message)
                self.assertFalse(Product.objects.filter(id=product.id).exists())

        forbidden_cases = [
            (self.enterprise_user_a, '企业用户不应能删除商品'),
            (self.temp_user_a, '临时用户不应能删除商品'),
        ]

        for user, message in forbidden_cases:
            with self.subTest(user=user.username, message=message):
                headers = self.get_token_for_user(user)
                url = reverse('delete-product', args=[self.product_a.id])
                response = self.client.delete(url, **headers)
                self.assertEqual(response.status_code, 403, message)

    def test_cross_enterprise_data_isolation(self):
        users = [self.enterprise_leader_a, self.enterprise_admin_a, self.enterprise_user_a]
        
        for user in users:
            with self.subTest(user=user.username):
                headers = self.get_token_for_user(user)
                
                response = self.client.get(reverse('get-products'), **headers)
                self.assertEqual(response.status_code, 200)
                products = json.loads(response.content)['products']
                product_ids = [p['id'] for p in products]
                self.assertIn(self.product_a.id, product_ids)
                self.assertNotIn(self.product_b.id, product_ids)

                detail_url = reverse('get-product-detail', args=[self.product_b.id])
                detail_response = self.client.get(detail_url, **headers)
                self.assertEqual(detail_response.status_code, 403)

                update_data = {'name': '尝试修改B商品'}
                update_url = reverse('update-product', args=[self.product_b.id])
                update_response = self.client.put(
                    update_url,
                    data=json.dumps(update_data),
                    content_type='application/json',
                    **headers
                )
                self.assertEqual(update_response.status_code, 403)

                delete_url = reverse('delete-product', args=[self.product_b.id])
                delete_response = self.client.delete(delete_url, **headers)
                self.assertEqual(delete_response.status_code, 403)

    def test_unauthenticated_access(self):
        endpoints = [
            ('get-products', None, 'get'),
            ('create-product', None, 'post'),
            ('get-product-detail', [self.product_a.id], 'get'),
            ('update-product', [self.product_a.id], 'put'),
            ('delete-product', [self.product_a.id], 'delete'),
        ]

        for url_name, args, method in endpoints:
            with self.subTest(endpoint=url_name):
                url = reverse(url_name, args=args)
                if method == 'get':
                    response = self.client.get(url)
                elif method == 'post':
                    response = self.client.post(url, data=json.dumps({}), content_type='application/json')
                elif method == 'put':
                    response = self.client.put(url, data=json.dumps({}), content_type='application/json')
                elif method == 'delete':
                    response = self.client.delete(url)
                self.assertEqual(response.status_code, 401)
