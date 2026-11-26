from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from datetime import datetime

from account.models import User, UserType
from store.models import Store, Order, OrderItem, OrderReceiver
from utils.decorators import jwt_required


@require_http_methods(['GET'])
@jwt_required
def get_orders(request, store_id):
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
        page_size = int(request.GET.get('page_size', 50))
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
@jwt_required
def get_order_detail(request, store_id, platform_order_id):
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
