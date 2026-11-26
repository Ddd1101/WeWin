from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
import traceback
from datetime import datetime

from account.models import User, UserType
from company.models import Company
from store.models import Store, Platform, Category, PlatformApiConfig, DataPullTask, StoreDataConfig, DataPullStatus
from store.services import BaseDataPullService, Ali1688DataPullService
from utils.decorators import jwt_required


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
@jwt_required
def get_stores(request):
    try:
        
        stores = []
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            stores = Store.objects.all()
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if request.user.company:
                stores = Store.objects.filter(company=request.user.company)
        elif request.user.user_type == UserType.ENTERPRISE_USER:
            stores = Store.objects.filter(managers=request.user)

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
@jwt_required
def create_store(request):
    try:
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if request.user.company:
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
        elif request.user.company:
            company = request.user.company
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
                created_by=request.user
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
@jwt_required
def update_store(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if request.user.company == store.company:
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
@jwt_required
def delete_store(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type == UserType.ENTERPRISE_LEADER:
            if request.user.company == store.company:
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
@jwt_required
def get_store_api_config(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if request.user.company == store.company:
                has_permission = True
        elif request.user.user_type == UserType.ENTERPRISE_USER:
            if request.user in store.managers.all():
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
@jwt_required
def create_or_update_api_config(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if request.user.company == store.company:
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
@jwt_required
def trigger_data_pull(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if request.user.company == store.company:
                has_permission = True
        elif request.user.user_type == UserType.ENTERPRISE_USER:
            if request.user in store.managers.all():
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
            params={'triggered_by': request.user.id}
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
@jwt_required
def get_pull_tasks(request, store_id):
    try:
        store = Store.objects.get(id=store_id)
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if request.user.company == store.company:
                has_permission = True
        elif request.user.user_type == UserType.ENTERPRISE_USER:
            if request.user in store.managers.all():
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
