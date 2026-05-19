from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
import json
import jwt
from django.conf import settings
from datetime import datetime, timedelta
from decimal import Decimal

from account.models import User, UserType
from company.models import Company
from .models import (
    Store, Platform, Category, Order, OrderItem, OrderReceiver,
    PlatformApiConfig, DataPullTask, StoreDataConfig, DataPullStatus,
    Product, ProductType, Bead, Accessory, FinishedProduct, FinishedProductBead, FinishedProductAccessory
)
from .services import BaseDataPullService, Ali1688DataPullService


def calculate_finished_product_cost(finished):
    """
    计算成品的总成本
    公式：串珠成本 + 配件成本 + 工费 + 弹性成本
    """
    total_cost = Decimal('0')
    
    # 计算串珠成本
    for fpb in finished.beads.all():
        total_cost += fpb.bead.product.cost_price * fpb.quantity
    
    # 计算配件成本
    for fpa in finished.accessories.all():
        total_cost += fpa.accessory.product.cost_price * fpa.quantity
    
    # 加上工费和弹性成本
    total_cost += finished.labor_cost
    total_cost += finished.elastic_cost
    
    return total_cost


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
            
            api_config = None
            try:
                config_obj = PlatformApiConfig.objects.filter(store=store).first()
                if config_obj:
                    api_config = {
                        'id': config_obj.id,
                        'app_key': config_obj.app_key,
                        'is_active': config_obj.is_active,
                        'has_access_token': bool(config_obj.access_token),
                        'has_refresh_token': bool(config_obj.refresh_token)
                    }
            except:
                pass
            
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
                'api_config': api_config,
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

            PlatformApiConfig.objects.create(
                store=store,
                app_key='',
                app_secret='',
                access_token='',
                refresh_token='',
                extra_config={},
                is_active=True
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


@require_http_methods(['GET'])
def get_store_api_config(request, store_id):
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
        elif current_user.user_type == UserType.ENTERPRISE_USER:
            if current_user in store.managers.all():
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限查看API配置'}, status=403)

        api_config = PlatformApiConfig.objects.filter(store=store).first()
        
        if api_config:
            return JsonResponse({
                'id': api_config.id,
                'store_id': api_config.store_id,
                'app_key': api_config.app_key,
                'access_token': api_config.access_token,
                'is_active': api_config.is_active,
                'extra_config': api_config.extra_config,
                'created_at': api_config.created_at.isoformat(),
                'updated_at': api_config.updated_at.isoformat()
            })
        else:
            return JsonResponse({'config': None})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Store.DoesNotExist:
        return JsonResponse({'error': '店铺不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_or_update_api_config(request, store_id):
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
            return JsonResponse({'error': '无权限配置API'}, status=403)

        data = json.loads(request.body)
        
        with transaction.atomic():
            api_config, created = PlatformApiConfig.objects.get_or_create(
                store=store,
                defaults={
                    'app_key': data.get('app_key', ''),
                    'app_secret': data.get('app_secret', ''),
                    'access_token': data.get('access_token', ''),
                    'refresh_token': data.get('refresh_token', ''),
                    'extra_config': data.get('extra_config', {}),
                    'is_active': data.get('is_active', True)
                }
            )
            
            if not created:
                if 'app_key' in data:
                    api_config.app_key = data['app_key']
                if 'app_secret' in data:
                    api_config.app_secret = data['app_secret']
                if 'access_token' in data:
                    api_config.access_token = data['access_token']
                if 'refresh_token' in data:
                    api_config.refresh_token = data['refresh_token']
                if 'extra_config' in data:
                    api_config.extra_config = data['extra_config']
                if 'is_active' in data:
                    api_config.is_active = data['is_active']
                api_config.save()

        return JsonResponse({
            'id': api_config.id,
            'store_id': api_config.store_id,
            'app_key': api_config.app_key,
            'is_active': api_config.is_active,
            'created': created
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
@require_http_methods(['POST'])
def trigger_data_pull(request, store_id):
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
        elif current_user.user_type == UserType.ENTERPRISE_USER:
            if current_user in store.managers.all():
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限触发数据拉取'}, status=403)

        data = json.loads(request.body)
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')
        
        if not start_time_str or not end_time_str:
            return JsonResponse({'error': '请指定拉取时间范围'}, status=400)
        
        try:
            start_time = datetime.fromisoformat(start_time_str)
            end_time = datetime.fromisoformat(end_time_str)
        except:
            return JsonResponse({'error': '时间格式错误'}, status=400)

        ServiceClass = BaseDataPullService.get_service_class(store.platform)
        if not ServiceClass:
            return JsonResponse({'error': f'不支持的平台: {store.platform}'}, status=400)

        service = ServiceClass(store)
        
        task = service.create_pull_task(
            task_type='order_pull',
            start_time=start_time,
            end_time=end_time,
            params={'triggered_by': current_user.id}
        )
        
        try:
            result = service.pull_orders(start_time, end_time, task)
            
            return JsonResponse({
                'task_id': task.id,
                'status': task.status,
                'stats': result.get('stats'),
                'request_logs': result.get('request_logs', [])
            })
        except Exception as e:
            request_logs = getattr(service, 'request_logs', [])
            return JsonResponse({
                'task_id': task.id,
                'error': str(e),
                'request_logs': request_logs
            }, status=500)
            
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Store.DoesNotExist:
        return JsonResponse({'error': '店铺不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_orders(request, store_id):
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
        elif current_user.user_type == UserType.ENTERPRISE_USER:
            if current_user in store.managers.all():
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限查看订单'}, status=403)

        order_status = request.GET.get('status')
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        orders = Order.objects.filter(store=store)
        
        if order_status:
            orders = orders.filter(order_status=order_status)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                orders = orders.filter(create_time__gte=start_dt)
            except:
                pass
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                orders = orders.filter(create_time__lte=end_dt)
            except:
                pass
        
        orders = orders.order_by('-create_time')
        
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        offset = (page - 1) * page_size
        
        total_count = orders.count()
        orders = orders[offset:offset + page_size]
        
        order_list = []
        for order in orders:
            items = []
            for item in order.items.all():
                items.append({
                    'id': item.id,
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'price': float(item.price),
                    'item_amount': float(item.item_amount),
                    'product_cargo_number': item.product_cargo_number
                })
            
            order_list.append({
                'id': order.id,
                'platform_order_id': order.platform_order_id,
                'platform_order_no': order.platform_order_no,
                'order_status': order.order_status,
                'order_status_display': order.get_order_status_display(),
                'refund_status': order.refund_status,
                'total_amount': float(order.total_amount),
                'sum_product_payment': float(order.sum_product_payment),
                'shipping_fee': float(order.shipping_fee),
                'refund_amount': float(order.refund_amount),
                'create_time': order.create_time.isoformat() if order.create_time else None,
                'pay_time': order.pay_time.isoformat() if order.pay_time else None,
                'buyer_login_id': order.buyer_login_id,
                'items': items
            })

        return JsonResponse({
            'orders': order_list,
            'total_count': total_count,
            'page': page,
            'page_size': page_size
        })
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Store.DoesNotExist:
        return JsonResponse({'error': '店铺不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_order_detail(request, store_id, platform_order_id):
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
        elif current_user.user_type == UserType.ENTERPRISE_USER:
            if current_user in store.managers.all():
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限查看订单详情'}, status=403)

        ServiceClass = BaseDataPullService.get_service_class(store.platform)
        if not ServiceClass:
            return JsonResponse({'error': f'不支持的平台: {store.platform}'}, status=400)

        service = ServiceClass(store)
        
        order_detail = service.pull_order_detail(platform_order_id)
        
        if order_detail:
            return JsonResponse({
                'success': True,
                'order_detail': order_detail
            })
        else:
            return JsonResponse({
                'success': False,
                'error': '未找到订单详情'
            }, status=404)
            
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Store.DoesNotExist:
        return JsonResponse({'error': '店铺不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_pull_tasks(request, store_id):
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
        elif current_user.user_type == UserType.ENTERPRISE_USER:
            if current_user in store.managers.all():
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限查看拉取任务'}, status=403)

        tasks = DataPullTask.objects.filter(store=store).order_by('-created_at')[:50]
        
        task_list = []
        for task in tasks:
            task_list.append({
                'id': task.id,
                'task_type': task.task_type,
                'status': task.status,
                'status_display': task.get_status_display(),
                'start_time': task.start_time.isoformat() if task.start_time else None,
                'end_time': task.end_time.isoformat() if task.end_time else None,
                'order_count': task.order_count,
                'new_order_count': task.new_order_count,
                'updated_order_count': task.updated_order_count,
                'error_message': task.error_message,
                'created_at': task.created_at.isoformat(),
                'updated_at': task.updated_at.isoformat()
            })

        return JsonResponse({'tasks': task_list})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Store.DoesNotExist:
        return JsonResponse({'error': '店铺不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_product_types(request):
    try:
        product_types = []
        for choice in ProductType.choices:
            product_types.append({'value': choice[0], 'label': choice[1]})
        return JsonResponse({'product_types': product_types})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_products(request):
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
        
        products = []
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            products = Product.objects.all()
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
            if current_user.company:
                products = Product.objects.filter(company=current_user.company)

        # 筛选条件
        product_type = request.GET.get('product_type')
        if product_type:
            products = products.filter(product_type=product_type)

        is_active = request.GET.get('is_active')
        if is_active is not None:
            products = products.filter(is_active=is_active == 'true')

        # 分页
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        offset = (page - 1) * page_size
        
        total_count = products.count()
        products = products[offset:offset + page_size]

        product_list = []
        for product in products:
            product_data = {
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'product_type': product.product_type,
                'product_type_display': product.get_product_type_display(),
                'cost_price': float(product.cost_price),
                'selling_price': float(product.selling_price),
                'location': product.location,
                'supplier': product.supplier,
                'company_id': product.company_id,
                'company_name': product.company.name,
                'image_url': request.build_absolute_uri(product.image.url) if product.image else None,
                'is_active': product.is_active,
                'created_by_id': product.created_by_id,
                'created_by_name': product.created_by.username if product.created_by else None,
                'created_at': product.created_at.isoformat(),
                'updated_at': product.updated_at.isoformat()
            }

            # 添加串珠、配件或成品特有属性
            if product.product_type == ProductType.BEAD:
                try:
                    bead = Bead.objects.get(product=product)
                    product_data['bead'] = {
                        'material': bead.material,
                        'size': bead.size,
                        'color': bead.color,
                        'weight': float(bead.weight),
                        'quality_level': bead.quality_level,
                        'remark': bead.remark
                    }
                except Bead.DoesNotExist:
                    pass
            elif product.product_type == ProductType.ACCESSORY:
                try:
                    accessory = Accessory.objects.get(product=product)
                    product_data['accessory'] = {
                        'material': accessory.material,
                        'size': accessory.size,
                        'color': accessory.color
                    }
                except Accessory.DoesNotExist:
                    pass
            elif product.product_type == ProductType.FINISHED:
                try:
                    finished = FinishedProduct.objects.get(product=product)
                    product_data['finished'] = {
                        'beads': [],
                        'accessories': [],
                        'labor_cost': float(finished.labor_cost),
                        'elastic_cost': float(finished.elastic_cost)
                    }
                    # 获取成品的串珠组成
                    for fpb in finished.beads.all():
                        bead_product = fpb.bead.product
                        bead = fpb.bead
                        product_data['finished']['beads'].append({
                            'bead_id': bead_product.id,
                            'bead_code': bead_product.code,
                            'bead_name': bead_product.name,
                            'bead_cost_price': float(bead_product.cost_price),
                            'bead_image_url': request.build_absolute_uri(bead_product.image.url) if bead_product.image else None,
                            'quantity': fpb.quantity,
                            'bead_weight': float(bead.weight),
                            'bead_quality_level': bead.quality_level,
                            'bead_remark': bead.remark
                        })
                    # 获取成品的配件组成
                    for fpa in finished.accessories.all():
                        acc_product = fpa.accessory.product
                        product_data['finished']['accessories'].append({
                            'accessory_id': acc_product.id,
                            'accessory_code': acc_product.code,
                            'accessory_name': acc_product.name,
                            'accessory_cost_price': float(acc_product.cost_price),
                            'accessory_image_url': request.build_absolute_uri(acc_product.image.url) if acc_product.image else None,
                            'quantity': fpa.quantity
                        })
                except FinishedProduct.DoesNotExist:
                    pass

            product_list.append(product_data)

        return JsonResponse({
            'products': product_list,
            'total_count': total_count,
            'page': page,
            'page_size': page_size
        })
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_product(request):
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
            return JsonResponse({'error': '无权限创建商品'}, status=403)

        # 支持 multipart/form-data 和 application/json 两种格式
        data_dict = {}
        image = None
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 从 POST 中获取普通字段数据
            for key in request.POST:
                data_dict[key] = request.POST[key]
            # 处理 JSON 字段，特别是 beads 和 accessories
            if 'beads' in request.POST:
                try:
                    data_dict['beads'] = json.loads(request.POST['beads'])
                except (json.JSONDecodeError, TypeError):
                    data_dict['beads'] = []
            if 'accessories' in request.POST:
                try:
                    data_dict['accessories'] = json.loads(request.POST['accessories'])
                except (json.JSONDecodeError, TypeError):
                    data_dict['accessories'] = []
            image = request.FILES.get('image')
        else:
            data_dict = json.loads(request.body)
            image = None

        code = data_dict.get('code')
        name = data_dict.get('name')
        product_type = data_dict.get('product_type')
        cost_price = data_dict.get('cost_price')
        selling_price = data_dict.get('selling_price')
        location = data_dict.get('location', '')
        supplier = data_dict.get('supplier', '')
        company_id = data_dict.get('company_id')

        if not all([code, name, product_type, cost_price, selling_price]):
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

        # 检查货号是否已存在
        if Product.objects.filter(code=code, company=company).exists():
            return JsonResponse({'error': '货号已存在'}, status=400)

        with transaction.atomic():
            product = Product.objects.create(
                code=code,
                name=name,
                product_type=product_type,
                cost_price=cost_price,
                selling_price=selling_price,
                location=location,
                supplier=supplier,
                company=company,
                image=image,
                created_by=current_user
            )

            # 创建串珠、配件或成品
            if product_type == ProductType.BEAD:
                Bead.objects.create(
                    product=product,
                    material=data_dict.get('material', ''),
                    size=data_dict.get('size', ''),
                    color=data_dict.get('color', ''),
                    weight=data_dict.get('weight', 0),
                    quality_level=data_dict.get('quality_level', 5),
                    remark=data_dict.get('remark', '')
                )
            elif product_type == ProductType.ACCESSORY:
                Accessory.objects.create(
                    product=product,
                    material=data_dict.get('material', ''),
                    size=data_dict.get('size', ''),
                    color=data_dict.get('color', '')
                )
            elif product_type == ProductType.FINISHED:
                finished = FinishedProduct.objects.create(
                    product=product,
                    labor_cost=data_dict.get('labor_cost', 0),
                    elastic_cost=data_dict.get('elastic_cost', 0)
                )
                # 添加串珠组成
                beads = data_dict.get('beads', [])
                for bead_data in beads:
                    try:
                        bead_product = Product.objects.get(
                            id=bead_data['bead_id'],
                            product_type=ProductType.BEAD,
                            company=company
                        )
                        bead = Bead.objects.get(product=bead_product)
                        FinishedProductBead.objects.create(
                            finished_product=finished,
                            bead=bead,
                            quantity=bead_data['quantity']
                        )
                    except (Product.DoesNotExist, Bead.DoesNotExist):
                        pass
                # 添加配件组成
                accessories = data_dict.get('accessories', [])
                for acc in accessories:
                    try:
                        accessory_product = Product.objects.get(
                            id=acc['accessory_id'],
                            product_type=ProductType.ACCESSORY,
                            company=company
                        )
                        accessory = Accessory.objects.get(product=accessory_product)
                        FinishedProductAccessory.objects.create(
                            finished_product=finished,
                            accessory=accessory,
                            quantity=acc['quantity']
                        )
                    except (Product.DoesNotExist, Accessory.DoesNotExist):
                        pass
                
                # 重新计算并保存成品的成本价格
                product.cost_price = calculate_finished_product_cost(finished)
                product.save()

        # 构建响应数据
        product_data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'product_type': product.product_type,
            'product_type_display': product.get_product_type_display(),
            'cost_price': float(product.cost_price),
            'selling_price': float(product.selling_price),
            'location': product.location,
            'supplier': product.supplier,
            'company_id': product.company_id,
            'company_name': product.company.name,
            'image_url': request.build_absolute_uri(product.image.url) if product.image else None,
            'is_active': product.is_active,
            'created_by_id': product.created_by_id,
            'created_by_name': product.created_by.username if product.created_by else None,
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat()
        }

        return JsonResponse(product_data, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['PUT', 'POST'])
def update_product(request, product_id):
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
        product = Product.objects.get(id=product_id)
        
        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if current_user.company == product.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限更新商品'}, status=403)

        # 支持 multipart/form-data 和 application/json 两种格式
        data_dict = {}
        image = None
        remove_image = False
        
        if request.content_type and 'multipart/form-data' in request.content_type:
            # 从 POST 中获取普通字段数据
            for key in request.POST:
                data_dict[key] = request.POST[key]
            # 处理 JSON 字段，特别是 beads 和 accessories
            if 'beads' in request.POST:
                try:
                    data_dict['beads'] = json.loads(request.POST['beads'])
                except (json.JSONDecodeError, TypeError):
                    data_dict['beads'] = []
            if 'accessories' in request.POST:
                try:
                    data_dict['accessories'] = json.loads(request.POST['accessories'])
                except (json.JSONDecodeError, TypeError):
                    data_dict['accessories'] = []
            image = request.FILES.get('image')
            remove_image_val = request.POST.get('remove_image', 'false').lower() == 'true'
        else:
            data_dict = json.loads(request.body)
            image = None
            remove_image = data_dict.get('remove_image', False)

        # 更新商品基本信息
        if 'name' in data_dict:
            product.name = data_dict['name']

        if 'cost_price' in data_dict:
            product.cost_price = data_dict['cost_price']

        if 'selling_price' in data_dict:
            product.selling_price = data_dict['selling_price']

        if 'location' in data_dict:
            product.location = data_dict['location']

        if 'supplier' in data_dict:
            product.supplier = data_dict['supplier']

        if 'is_active' in data_dict:
            product.is_active = data_dict['is_active']

        # 处理图片
        use_remove_image = remove_image_val if request.content_type and 'multipart/form-data' in request.content_type else remove_image
        if use_remove_image:
            if product.image:
                product.image.delete()
                product.image = None
        elif image:
            if product.image:
                product.image.delete()
            product.image = image

        product.save()

        # 更新串珠、配件或成品信息
        if product.product_type == ProductType.BEAD:
            try:
                bead = Bead.objects.get(product=product)
                if 'material' in data_dict:
                    bead.material = data_dict['material']
                if 'size' in data_dict:
                    bead.size = data_dict['size']
                if 'color' in data_dict:
                    bead.color = data_dict['color']
                if 'weight' in data_dict:
                    bead.weight = data_dict['weight']
                if 'quality_level' in data_dict:
                    bead.quality_level = data_dict['quality_level']
                if 'remark' in data_dict:
                    bead.remark = data_dict['remark']
                bead.save()
            except Bead.DoesNotExist:
                pass
        elif product.product_type == ProductType.ACCESSORY:
            try:
                accessory = Accessory.objects.get(product=product)
                if 'material' in data_dict:
                    accessory.material = data_dict['material']
                if 'size' in data_dict:
                    accessory.size = data_dict['size']
                if 'color' in data_dict:
                    accessory.color = data_dict['color']
                accessory.save()
            except Accessory.DoesNotExist:
                pass
        elif product.product_type == ProductType.FINISHED:
            try:
                finished = FinishedProduct.objects.get(product=product)
                # 更新工费和弹性成本
                if 'labor_cost' in data_dict:
                    finished.labor_cost = data_dict['labor_cost']
                if 'elastic_cost' in data_dict:
                    finished.elastic_cost = data_dict['elastic_cost']
                finished.save()

                # 更新串珠组成
                if 'beads' in data_dict:
                    # 先删除现有的串珠组成
                    FinishedProductBead.objects.filter(finished_product=finished).delete()
                    # 添加新的串珠组成
                    beads = data_dict['beads']
                    for bead_data in beads:
                        try:
                            bead_product = Product.objects.get(
                                id=bead_data['bead_id'],
                                product_type=ProductType.BEAD,
                                company=product.company
                            )
                            bead = Bead.objects.get(product=bead_product)
                            FinishedProductBead.objects.create(
                                finished_product=finished,
                                bead=bead,
                                quantity=bead_data['quantity']
                            )
                        except (Product.DoesNotExist, Bead.DoesNotExist):
                            pass

                # 更新配件组成
                if 'accessories' in data_dict:
                    # 先删除现有的配件组成
                    FinishedProductAccessory.objects.filter(finished_product=finished).delete()
                    # 添加新的配件组成
                    accessories = data_dict['accessories']
                    for acc in accessories:
                        try:
                            accessory_product = Product.objects.get(
                                id=acc['accessory_id'],
                                product_type=ProductType.ACCESSORY,
                                company=product.company
                            )
                            accessory = Accessory.objects.get(product=accessory_product)
                            FinishedProductAccessory.objects.create(
                                finished_product=finished,
                                accessory=accessory,
                                quantity=acc['quantity']
                            )
                        except (Product.DoesNotExist, Accessory.DoesNotExist):
                            pass
                
                # 重新计算并保存成品的成本价格
                product.cost_price = calculate_finished_product_cost(finished)
                product.save()
            except FinishedProduct.DoesNotExist:
                pass

        # 构建响应数据
        product_data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'product_type': product.product_type,
            'product_type_display': product.get_product_type_display(),
            'cost_price': float(product.cost_price),
            'selling_price': float(product.selling_price),
            'location': product.location,
            'supplier': product.supplier,
            'company_id': product.company_id,
            'company_name': product.company.name,
            'image_url': request.build_absolute_uri(product.image.url) if product.image else None,
            'is_active': product.is_active,
            'created_by_id': product.created_by_id,
            'created_by_name': product.created_by.username if product.created_by else None,
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat()
        }

        return JsonResponse(product_data)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({'error': '商品不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['DELETE'])
def delete_product(request, product_id):
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
        product = Product.objects.get(id=product_id)
        
        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type == UserType.ENTERPRISE_LEADER:
            if current_user.company == product.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限删除商品'}, status=403)

        product.delete()
        return JsonResponse({'message': '商品删除成功'})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({'error': '商品不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_product_detail(request, product_id):
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
        product = Product.objects.get(id=product_id)
        
        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
            if current_user.company == product.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限查看商品详情'}, status=403)

        product_data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'product_type': product.product_type,
            'product_type_display': product.get_product_type_display(),
            'cost_price': float(product.cost_price),
            'selling_price': float(product.selling_price),
            'location': product.location,
            'supplier': product.supplier,
            'company_id': product.company_id,
            'company_name': product.company.name,
            'image_url': request.build_absolute_uri(product.image.url) if product.image else None,
            'is_active': product.is_active,
            'created_by_id': product.created_by_id,
            'created_by_name': product.created_by.username if product.created_by else None,
            'created_at': product.created_at.isoformat(),
            'updated_at': product.updated_at.isoformat()
        }

        # 添加串珠、配件或成品特有属性
        if product.product_type == ProductType.BEAD:
            try:
                bead = Bead.objects.get(product=product)
                product_data['bead'] = {
                    'material': bead.material,
                    'size': bead.size,
                    'color': bead.color,
                    'weight': float(bead.weight),
                    'quality_level': bead.quality_level,
                    'remark': bead.remark
                }
            except Bead.DoesNotExist:
                pass
        elif product.product_type == ProductType.ACCESSORY:
            try:
                accessory = Accessory.objects.get(product=product)
                product_data['accessory'] = {
                    'material': accessory.material,
                    'size': accessory.size,
                    'color': accessory.color
                }
            except Accessory.DoesNotExist:
                pass
        elif product.product_type == ProductType.FINISHED:
            try:
                finished = FinishedProduct.objects.get(product=product)
                product_data['finished'] = {
                    'beads': [],
                    'accessories': [],
                    'labor_cost': float(finished.labor_cost),
                    'elastic_cost': float(finished.elastic_cost)
                }
                # 获取成品的串珠组成
                for fpb in finished.beads.all():
                    bead_product = fpb.bead.product
                    bead = fpb.bead
                    product_data['finished']['beads'].append({
                        'bead_id': bead_product.id,
                        'bead_code': bead_product.code,
                        'bead_name': bead_product.name,
                        'bead_cost_price': float(bead_product.cost_price),
                        'bead_image_url': request.build_absolute_uri(bead_product.image.url) if bead_product.image else None,
                        'quantity': fpb.quantity,
                        'bead_weight': float(bead.weight),
                        'bead_quality_level': bead.quality_level,
                        'bead_remark': bead.remark
                    })
                # 获取成品的配件组成
                for fpa in finished.accessories.all():
                    acc_product = fpa.accessory.product
                    product_data['finished']['accessories'].append({
                        'accessory_id': acc_product.id,
                        'accessory_code': acc_product.code,
                        'accessory_name': acc_product.name,
                        'accessory_cost_price': float(acc_product.cost_price),
                        'accessory_image_url': request.build_absolute_uri(acc_product.image.url) if acc_product.image else None,
                        'quantity': fpa.quantity
                    })
            except FinishedProduct.DoesNotExist:
                pass

        return JsonResponse(product_data)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({'error': '商品不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_accessories(request):
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
        
        accessories = []
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            accessories = Accessory.objects.all()
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
            if current_user.company:
                accessories = Accessory.objects.filter(product__company=current_user.company)

        accessory_list = []
        for accessory in accessories:
            product = accessory.product
            accessory_list.append({
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'cost_price': float(product.cost_price),
                'location': product.location,
                'supplier': product.supplier,
                'material': accessory.material,
                'size': accessory.size,
                'color': accessory.color
            })

        return JsonResponse({'accessories': accessory_list})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_beads(request):
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
        
        beads = []
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            beads = Bead.objects.all()
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
            if current_user.company:
                beads = Bead.objects.filter(product__company=current_user.company)

        bead_list = []
        for bead in beads:
            product = bead.product
            bead_list.append({
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'cost_price': float(product.cost_price),
                'location': product.location,
                'supplier': product.supplier,
                'material': bead.material,
                'size': bead.size,
                'color': bead.color,
                'weight': float(bead.weight),
                'quality_level': bead.quality_level,
                'remark': bead.remark
            })

        return JsonResponse({'beads': bead_list})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
