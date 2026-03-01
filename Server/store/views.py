from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
import jwt
from django.conf import settings

from account.models import User, UserType
from company.models import Company
from .models import Store, Platform, Category


SECRET_KEY = settings.SECRET_KEY


@require_http_methods(['GET'])
def get_platforms(request):
    try:
        platforms = []
        for choice in Platform.choices:
            platforms.append({'value': choice[0], 'label': choice[1]})
        return JsonResponse({'platforms': platforms})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_categories(request):
    try:
        categories = []
        for choice in Category.choices:
            categories.append({'value': choice[0], 'label': choice[1]})
        return JsonResponse({'categories': categories})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_stores(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        stores = []
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            stores = Store.objects.all()
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if current_user.company:
                stores = Store.objects.filter(company=current_user.company)
        elif current_user.user_type == UserType.ENTERPRISE_USER:
            stores = Store.objects.filter(managers=current_user)

        store_list = []
        for store in stores:
            managers = []
            for manager in store.managers.all():
                managers.append({
                    'id': manager.id,
                    'username': manager.username,
                    'real_name': manager.real_name
                })
            store_list.append({
                'id': store.id,
                'name': store.name,
                'platform': store.platform,
                'platform_display': store.get_platform_display(),
                'category': store.category,
                'category_display': store.get_category_display(),
                'company_id': store.company_id,
                'company_name': store.company.name,
                'managers': managers,
                'description': store.description,
                'shop_url': store.shop_url,
                'contact_name': store.contact_name,
                'contact_phone': store.contact_phone,
                'is_active': store.is_active,
                'created_by_id': store.created_by_id,
                'created_by_name': store.created_by.username if store.created_by else None,
                'created_at': store.created_at.isoformat(),
                'updated_at': store.updated_at.isoformat()
            })

        return JsonResponse({'stores': store_list})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_store(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if current_user.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限创建店铺'}, status=403)

        data = json.loads(request.body)
        name = data.get('name')
        platform = data.get('platform')
        category = data.get('category')
        company_id = data.get('company_id')
        manager_ids = data.get('manager_ids', [])
        description = data.get('description', '')
        shop_url = data.get('shop_url', '')
        contact_name = data.get('contact_name', '')
        contact_phone = data.get('contact_phone', '')

        if not all([name, platform, category]):
            return JsonResponse({'error': '必填字段不能为空'}, status=400)

        company = None
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return JsonResponse({'error': '企业不存在'}, status=404)
        elif current_user.company:
            company = current_user.company
        else:
            return JsonResponse({'error': '请选择所属企业'}, status=400)

        with transaction.atomic():
            store = Store.objects.create(
                name=name,
                platform=platform,
                category=category,
                company=company,
                description=description,
                shop_url=shop_url,
                contact_name=contact_name,
                contact_phone=contact_phone,
                created_by=current_user
            )

            if manager_ids:
                managers = User.objects.filter(id__in=manager_ids, company=company)
                store.managers.add(*managers)

        managers = []
        for manager in store.managers.all():
            managers.append({
                'id': manager.id,
                'username': manager.username,
                'real_name': manager.real_name
            })

        return JsonResponse({
            'id': store.id,
            'name': store.name,
            'platform': store.platform,
            'platform_display': store.get_platform_display(),
            'category': store.category,
            'category_display': store.get_category_display(),
            'company_id': store.company_id,
            'company_name': store.company.name,
            'managers': managers,
            'description': store.description,
            'shop_url': store.shop_url,
            'contact_name': store.contact_name,
            'contact_phone': store.contact_phone,
            'is_active': store.is_active,
            'created_by_id': store.created_by_id,
            'created_by_name': store.created_by.username if store.created_by else None,
            'created_at': store.created_at.isoformat(),
            'updated_at': store.updated_at.isoformat()
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['PUT'])
def update_store(request, store_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        store = Store.objects.get(id=store_id)
        
        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if current_user.company == store.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限更新店铺'}, status=403)

        data = json.loads(request.body)

        if 'name' in data:
            store.name = data['name']

        if 'platform' in data:
            store.platform = data['platform']

        if 'category' in data:
            store.category = data['category']

        if 'description' in data:
            store.description = data['description']

        if 'shop_url' in data:
            store.shop_url = data['shop_url']

        if 'contact_name' in data:
            store.contact_name = data['contact_name']

        if 'contact_phone' in data:
            store.contact_phone = data['contact_phone']

        if 'is_active' in data:
            store.is_active = data['is_active']

        if 'manager_ids' in data:
            manager_ids = data['manager_ids']
            store.managers.clear()
            if manager_ids:
                managers = User.objects.filter(id__in=manager_ids, company=store.company)
                store.managers.add(*managers)

        store.save()

        managers = []
        for manager in store.managers.all():
            managers.append({
                'id': manager.id,
                'username': manager.username,
                'real_name': manager.real_name
            })

        return JsonResponse({
            'id': store.id,
            'name': store.name,
            'platform': store.platform,
            'platform_display': store.get_platform_display(),
            'category': store.category,
            'category_display': store.get_category_display(),
            'company_id': store.company_id,
            'company_name': store.company.name,
            'managers': managers,
            'description': store.description,
            'shop_url': store.shop_url,
            'contact_name': store.contact_name,
            'contact_phone': store.contact_phone,
            'is_active': store.is_active,
            'created_by_id': store.created_by_id,
            'created_by_name': store.created_by.username if store.created_by else None,
            'created_at': store.created_at.isoformat(),
            'updated_at': store.updated_at.isoformat()
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Store.DoesNotExist:
        return JsonResponse({'error': '店铺不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['DELETE'])
def delete_store(request, store_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        store = Store.objects.get(id=store_id)
        
        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type == UserType.ENTERPRISE_LEADER:
            if current_user.company == store.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限删除店铺'}, status=403)

        store.delete()
        return JsonResponse({'message': '店铺删除成功'})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Store.DoesNotExist:
        return JsonResponse({'error': '店铺不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
