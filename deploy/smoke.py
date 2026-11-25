#!/usr/bin/env python3
"""Live HTTPS checks confined to disposable companies; always run cleanup."""
import argparse
import io
import json
import os
from pathlib import Path
import secrets
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Server'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wewin.settings')
import django
django.setup()
from PIL import Image
import requests
from account.models import User, UserType
from company.models import Company
from store.models import Product, Store, FinishedProduct
from django.core.files.storage import default_storage
from utils.write_lock import write_lock


def prepare(state):
    if state.exists():
        raise RuntimeError('State exists; reuse or clean it first')
    suffix = secrets.token_hex(6)
    data = {'username': 'deployment-' + suffix, 'password': secrets.token_urlsafe(32), 'companies': []}
    state.write_text(json.dumps(data))
    with write_lock():
        for index in range(2):
            company = Company.objects.create(name='Deployment validation ' + suffix + str(index), code='validation-' + suffix + str(index))
            data['companies'].append(company.pk)
            state.write_text(json.dumps(data))
        User.objects.create_user(username=data['username'], password=data['password'], company_id=data['companies'][0], user_type=UserType.ENTERPRISE_LEADER)
        user2 = User.objects.create_user(username=data['username'] + '-other', password=data['password'], company_id=data['companies'][1], user_type=UserType.ENTERPRISE_LEADER)
        data['other_username'] = user2.username
        store = Store.objects.create(name='Validation store', company_id=data['companies'][0], platform='1688')
        data['store'] = store.pk
        state.write_text(json.dumps(data))
    print('Disposable validation tenants prepared')


def run(state, base):
    data = json.loads(state.read_text())
    session = requests.Session()
    timings = []
    def call(method, path, expect=200, **kwargs):
        start = time.monotonic()
        response = session.request(method, base + path, timeout=10, **kwargs)
        timings.append(round((time.monotonic() - start) * 1000, 1))
        if response.status_code != expect:
            raise AssertionError('%s %s: expected %s got %s' % (method, path, expect, response.status_code))
        return response
    result = call('POST', '/api/account/login/', json={'username': data['username'], 'password': data['password']}).json()
    session.headers['Authorization'] = 'Bearer ' + result['token']
    image = io.BytesIO()
    Image.new('RGB', (16, 16), 'blue').save(image, format='PNG')
    product = call('POST', '/api/store/products/create/', expect=201, data={'name': 'Deployment image check', 'code': data['username'], 'product_type': 'accessory', 'selling_price': '19.50'}, files={'image': ('check.png', image.getvalue(), 'image/png')}).json()
    product_id = product['id']
    data['product'] = product_id
    state.write_text(json.dumps(data))
    first = product['image_url']
    assert first.startswith(base + '/media/products/')
    assert requests.get(first, timeout=10).content == image.getvalue()
    call('GET', '/api/store/products/')
    call('GET', '/api/store/products/%s/detail/' % product_id)
    call('GET', '/api/store/%s/orders/' % data['store'])
    customer = call('POST', '/api/customer/create/', expect=201, json={'name': 'Deployment quote check'}).json()
    call('POST', '/api/customer/%s/products/create-or-update/' % customer['id'], json={'product_id': product_id, 'price': '21.35'})
    call('GET', '/api/customer/%s/products/' % customer['id'])
    replaced = call('POST', '/api/store/products/%s/update/' % product_id, files={'image': ('new.png', image.getvalue(), 'image/png')}).json()
    assert replaced['image_url'] != first
    assert requests.get(first, timeout=10).status_code == 404
    assert requests.get(replaced['image_url'], timeout=10).content == image.getvalue()
    call('POST', '/api/store/products/%s/update/' % product_id, expect=400, files={'image': ('bad.jpg', b'not-an-image', 'image/jpeg')})
    data['image_url'] = replaced['image_url']
    state.write_text(json.dumps(data))
    finished = call('POST', '/api/store/products/create/', expect=201, json={
        'name': 'Deployment BOM check', 'code': data['username'] + '-finished',
        'product_type': 'finished', 'selling_price': '39.00',
        'accessories': [{'accessory_id': product_id, 'quantity': 2}],
    }).json()
    detail = call('GET', '/api/store/products/%s/detail/' % finished['id']).json()
    assert detail['finished']['accessories'][0]['accessory_image_url'] == replaced['image_url']
    other = requests.post(base + '/api/account/login/', json={'username': data['other_username'], 'password': data['password']}, timeout=10).json()
    response = requests.get(base + '/api/store/products/%s/detail/' % product_id, headers={'Authorization': 'Bearer ' + other['token']}, timeout=10)
    assert response.status_code == 403
    print(json.dumps({'checks': 'login/products/orders/quotes/images/BOM/isolation', 'requests': len(timings), 'max_ms': max(timings), 'median_ms': sorted(timings)[len(timings)//2]}))


def cleanup(state):
    data = json.loads(state.read_text())
    with write_lock():
        for product in Product.objects.filter(company_id__in=data['companies']):
            if product.image:
                default_storage.delete(product.image.name)
        FinishedProduct.objects.filter(product__company_id__in=data['companies']).delete()
        Company.objects.filter(pk__in=data['companies']).delete()
        User.objects.filter(username__in=[data['username'], data['username'] + '-other']).delete()
    state.unlink()
    print('Disposable validation tenants removed')


if __name__ == '__main__':
    os.umask(0o077)
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['prepare', 'run', 'cleanup'])
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--base', default='https://47.250.165.79')
    args = parser.parse_args()
    if args.action == 'run':
        run(args.state, args.base.rstrip('/'))
    else:
        globals()[args.action](args.state)
