from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.utils import timezone
import json
import jwt
from decimal import Decimal
from datetime import datetime, timedelta
from account.models import User, UserType
from store.models import Product, ProductSku
from .models import (
    PurchaseList, PurchaseItem,
    PurchaseListStatus, PurchaseItemStatus,
)


SECRET_KEY = settings.SECRET_KEY


def authenticate_jwt(request):
    """
    JWT 认证验证辅助函数
    返回 (current_user, error_response)
    如果认证成功，error_response 为 None
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, JsonResponse({'error': '未授权'}, status=401)

    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None, JsonResponse({'error': 'Token已过期'}, status=401)
    except jwt.InvalidTokenError:
        return None, JsonResponse({'error': '无效的Token'}, status=401)

    try:
        current_user = User.objects.get(id=payload['user_id'])
        return current_user, None
    except User.DoesNotExist:
        return None, JsonResponse({'error': '用户不存在'}, status=404)


def purchase_item_to_dict(item):
    """将采购项对象转换为字典"""
    return {
        'id': item.id,
        'purchase_list_id': item.purchase_list_id,
        'product_id': item.product_id,
        'sku_id': item.sku_id,
        'product_type': item.product_type,
        'product_name': item.product_name,
        'sku_code': item.sku_code,
        'quantity': float(item.quantity),
        'unit': item.unit,
        'unit_price': float(item.unit_price),
        'supplier': item.supplier,
        'location': item.location,
        'quality_level': item.quality_level,
        'material': item.material,
        'size': item.size,
        'color': item.color,
        'remark': item.remark,
        'status': item.status,
        'status_display': item.get_status_display(),
        'purchased_quantity': float(item.purchased_quantity),
        'created_at': item.created_at.isoformat(),
        'updated_at': item.updated_at.isoformat(),
    }


def purchase_list_to_dict(pl, include_items=True):
    """将采购清单对象转换为字典"""
    items = list(pl.items.all())
    total_count = len(items)
    purchased_count = sum(1 for it in items if it.status == PurchaseItemStatus.PURCHASED)
    result = {
        'id': pl.id,
        'title': pl.title,
        'status': pl.status,
        'status_display': pl.get_status_display(),
        'planned_date': pl.planned_date.isoformat(),
        'notes': pl.notes,
        'company_id': pl.company_id,
        'assignee_id': pl.assignee_id,
        'assignee_name': pl.assignee.username if pl.assignee else None,
        'created_by_id': pl.created_by_id,
        'created_by_name': pl.created_by.username if pl.created_by else None,
        'created_at': pl.created_at.isoformat(),
        'updated_at': pl.updated_at.isoformat(),
        'total_count': total_count,
        'purchased_count': purchased_count,
    }
    if include_items:
        result['items'] = [purchase_item_to_dict(it) for it in items]
    return result


def check_list_company_permission(current_user, purchase_list):
    """检查用户是否可访问该清单（企业隔离）"""
    if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
        return True
    if current_user.company_id is None:
        return False
    return current_user.company_id == purchase_list.company_id


def check_list_edit_permission(current_user, purchase_list):
    """检查用户是否可编辑清单项（created_by 或 assignee）"""
    if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
        return True
    if purchase_list.created_by_id == current_user.id:
        return True
    if purchase_list.assignee_id is not None and purchase_list.assignee_id == current_user.id:
        return True
    return False


def build_item_from_data(purchase_list, data):
    """根据请求数据构建采购项（未保存）"""
    product_id = data.get('product_id')
    sku_id = data.get('sku_id')
    product = None
    sku = None
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            product = None
    if sku_id:
        try:
            sku = ProductSku.objects.get(id=sku_id)
        except ProductSku.DoesNotExist:
            sku = None

    quality_level = data.get('quality_level')
    size = data.get('size')

    return PurchaseItem(
        purchase_list=purchase_list,
        product=product,
        sku=sku,
        product_type=data.get('product_type', ''),
        product_name=data.get('product_name', ''),
        sku_code=data.get('sku_code', ''),
        quantity=Decimal(str(data.get('quantity', 0))),
        unit=data.get('unit', '克'),
        unit_price=Decimal(str(data.get('unit_price', 0))),
        supplier=data.get('supplier', ''),
        location=data.get('location', ''),
        quality_level=quality_level if quality_level not in (None, '') else None,
        material=data.get('material', ''),
        size=size if size not in (None, '') else None,
        color=data.get('color', ''),
        remark=data.get('remark', ''),
    )


@require_http_methods(['GET'])
def get_purchase_lists(request):
    """获取采购清单列表"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        # 企业隔离
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            qs = PurchaseList.objects.all()
        else:
            if current_user.company_id:
                qs = PurchaseList.objects.filter(company_id=current_user.company_id)
            else:
                qs = PurchaseList.objects.none()

        # 负责人范围
        assignee_scope = request.GET.get('assignee_scope', 'my_assigned')
        if assignee_scope == 'mine':
            qs = qs.filter(created_by=current_user)
        elif assignee_scope == 'my_assigned':
            qs = qs.filter(assignee=current_user)
        # 'all' 不附加额外过滤

        # 状态过滤
        status = request.GET.get('status')
        if status:
            qs = qs.filter(status=status)

        # 分页
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
        offset = (page - 1) * page_size

        total_count = qs.count()
        qs = qs[offset:offset + page_size]

        lists = [purchase_list_to_dict(pl, include_items=False) for pl in qs]

        return JsonResponse({
            'lists': lists,
            'total_count': total_count,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_purchase_list(request):
    """创建采购清单"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        data = json.loads(request.body)
        title = data.get('title')
        assignee_id = data.get('assignee_id')
        planned_date_str = data.get('planned_date')
        notes = data.get('notes', '')
        items_data = data.get('items', [])

        # 校验
        if not title:
            return JsonResponse({'error': '清单标题不能为空'}, status=400)
        if not assignee_id:
            return JsonResponse({'error': '采购负责人不能为空'}, status=400)
        if not items_data:
            return JsonResponse({'error': '采购项不能为空'}, status=400)
        if not planned_date_str:
            return JsonResponse({'error': '计划采购日期不能为空'}, status=400)

        try:
            planned_date = datetime.strptime(planned_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return JsonResponse({'error': '计划日期格式无效，应为 YYYY-MM-DD'}, status=400)

        # 校验负责人存在且同企业
        try:
            assignee = User.objects.get(id=assignee_id)
        except User.DoesNotExist:
            return JsonResponse({'error': '采购负责人不存在'}, status=404)

        if current_user.company_id is not None and assignee.company_id != current_user.company_id:
            return JsonResponse({'error': '采购负责人不属于同一企业'}, status=400)

        with transaction.atomic():
            purchase_list = PurchaseList.objects.create(
                title=title,
                assignee=assignee,
                planned_date=planned_date,
                notes=notes,
                created_by=current_user,
                company=current_user.company,
                status=PurchaseListStatus.PENDING,
            )

            for item_data in items_data:
                item = build_item_from_data(purchase_list, item_data)
                item.save()

        # 重新获取以包含 items
        purchase_list = PurchaseList.objects.get(id=purchase_list.id)
        return JsonResponse(purchase_list_to_dict(purchase_list, include_items=True), status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_purchase_list_detail(request, list_id):
    """获取采购清单详情"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        try:
            purchase_list = PurchaseList.objects.get(id=list_id)
        except PurchaseList.DoesNotExist:
            return JsonResponse({'error': '采购清单不存在'}, status=404)

        if not check_list_company_permission(current_user, purchase_list):
            return JsonResponse({'error': '无权限查看该采购清单'}, status=403)

        return JsonResponse(purchase_list_to_dict(purchase_list, include_items=True))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['PUT'])
def update_purchase_list(request, list_id):
    """编辑采购清单基本信息（仅创建人可调用）"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        try:
            purchase_list = PurchaseList.objects.get(id=list_id)
        except PurchaseList.DoesNotExist:
            return JsonResponse({'error': '采购清单不存在'}, status=404)

        # 仅创建人可调用
        if purchase_list.created_by_id != current_user.id:
            return JsonResponse({'error': '无权限编辑该采购清单'}, status=403)

        data = json.loads(request.body)

        if 'title' in data:
            if not data['title']:
                return JsonResponse({'error': '清单标题不能为空'}, status=400)
            purchase_list.title = data['title']

        if 'assignee_id' in data:
            assignee_id = data['assignee_id']
            if assignee_id:
                try:
                    assignee = User.objects.get(id=assignee_id)
                except User.DoesNotExist:
                    return JsonResponse({'error': '采购负责人不存在'}, status=404)
                if current_user.company_id is not None and assignee.company_id != current_user.company_id:
                    return JsonResponse({'error': '采购负责人不属于同一企业'}, status=400)
                purchase_list.assignee = assignee
            else:
                purchase_list.assignee = None

        if 'planned_date' in data:
            try:
                purchase_list.planned_date = datetime.strptime(data['planned_date'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return JsonResponse({'error': '计划日期格式无效，应为 YYYY-MM-DD'}, status=400)

        if 'notes' in data:
            purchase_list.notes = data['notes']

        purchase_list.save()

        # 重新获取以包含 items
        purchase_list = PurchaseList.objects.get(id=list_id)
        return JsonResponse(purchase_list_to_dict(purchase_list, include_items=True))
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except PurchaseList.DoesNotExist:
        return JsonResponse({'error': '采购清单不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def add_purchase_item(request, list_id):
    """向已有清单追加单个采购项（created_by 或 assignee 可调用）"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        try:
            purchase_list = PurchaseList.objects.get(id=list_id)
        except PurchaseList.DoesNotExist:
            return JsonResponse({'error': '采购清单不存在'}, status=404)

        if not check_list_edit_permission(current_user, purchase_list):
            return JsonResponse({'error': '无权限操作该采购清单'}, status=403)

        data = json.loads(request.body)

        with transaction.atomic():
            item = build_item_from_data(purchase_list, data)
            item.save()

        purchase_list = PurchaseList.objects.get(id=list_id)
        return JsonResponse(purchase_list_to_dict(purchase_list, include_items=True), status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_uncompleted_lists(request):
    """获取当前用户相关的未完成清单（供"加入已有清单"选择）"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        # 企业隔离
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            qs = PurchaseList.objects.all()
        else:
            if current_user.company_id:
                qs = PurchaseList.objects.filter(company_id=current_user.company_id)
            else:
                qs = PurchaseList.objects.none()

        # 未完成 且 与当前用户相关
        qs = qs.exclude(status=PurchaseListStatus.COMPLETED)
        qs = qs.filter(Q(created_by=current_user) | Q(assignee=current_user))

        lists = []
        for pl in qs:
            lists.append({
                'id': pl.id,
                'title': pl.title,
                'planned_date': pl.planned_date.isoformat(),
                'status': pl.status,
                'status_display': pl.get_status_display(),
                'assignee_name': pl.assignee.username if pl.assignee else None,
            })

        return JsonResponse({'lists': lists})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def mark_item_purchased(request, item_id):
    """标记采购项已购买"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        try:
            item = PurchaseItem.objects.select_related('purchase_list').get(id=item_id)
        except PurchaseItem.DoesNotExist:
            return JsonResponse({'error': '采购项不存在'}, status=404)

        purchase_list = item.purchase_list
        if not check_list_edit_permission(current_user, purchase_list):
            return JsonResponse({'error': '无权限操作该采购项'}, status=403)

        with transaction.atomic():
            item.status = PurchaseItemStatus.PURCHASED
            item.purchased_quantity = item.quantity
            item.save()

            # 检查并更新清单状态：若所有 items 都是 PURCHASED，则清单 COMPLETED
            all_purchased = not purchase_list.items.exclude(
                status=PurchaseItemStatus.PURCHASED
            ).exists()
            if all_purchased:
                purchase_list.status = PurchaseListStatus.COMPLETED
                purchase_list.save(update_fields=['status', 'updated_at'])

        return JsonResponse({
            'item': purchase_item_to_dict(item),
            'list_status': purchase_list.status,
            'list_status_display': purchase_list.get_status_display(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def mark_item_partial(request, item_id):
    """标记采购项已购买部分"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        try:
            item = PurchaseItem.objects.select_related('purchase_list').get(id=item_id)
        except PurchaseItem.DoesNotExist:
            return JsonResponse({'error': '采购项不存在'}, status=404)

        purchase_list = item.purchase_list
        if not check_list_edit_permission(current_user, purchase_list):
            return JsonResponse({'error': '无权限操作该采购项'}, status=403)

        data = json.loads(request.body)
        purchased_quantity = data.get('purchased_quantity')
        if purchased_quantity is None:
            return JsonResponse({'error': '已购买数量不能为空'}, status=400)

        with transaction.atomic():
            item.purchased_quantity = Decimal(str(purchased_quantity))
            item.status = PurchaseItemStatus.PARTIALLY_PURCHASED
            item.save()

            # 清单若 PENDING 则变 IN_PROGRESS
            if purchase_list.status == PurchaseListStatus.PENDING:
                purchase_list.status = PurchaseListStatus.IN_PROGRESS
                purchase_list.save(update_fields=['status', 'updated_at'])

        return JsonResponse({
            'item': purchase_item_to_dict(item),
            'list_status': purchase_list.status,
            'list_status_display': purchase_list.get_status_display(),
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def carry_over_next_day(request, item_id):
    """添加到下一日采购清单"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        try:
            original_item = PurchaseItem.objects.select_related('purchase_list').get(id=item_id)
        except PurchaseItem.DoesNotExist:
            return JsonResponse({'error': '采购项不存在'}, status=404)

        original_list = original_item.purchase_list
        if not check_list_edit_permission(current_user, original_list):
            return JsonResponse({'error': '无权限操作该采购项'}, status=403)

        # 计算剩余数量
        remaining = original_item.quantity - original_item.purchased_quantity
        if remaining <= 0:
            return JsonResponse({'error': '该项已完成，无需添加到下一日'}, status=400)

        tomorrow = (timezone.now() + timedelta(days=1)).date()

        with transaction.atomic():
            # 创建或复用下一日清单
            new_list = PurchaseList.objects.filter(
                planned_date=tomorrow,
                assignee=original_list.assignee,
                created_by=current_user,
                company=original_list.company,
            ).first()

            if not new_list:
                new_list = PurchaseList.objects.create(
                    title=f"采购清单 {tomorrow.isoformat()}",
                    planned_date=tomorrow,
                    assignee=original_list.assignee,
                    created_by=current_user,
                    company=original_list.company,
                    status=PurchaseListStatus.PENDING,
                    notes='',
                )

            # 复制原 item 字段到新 item
            new_item = PurchaseItem.objects.create(
                purchase_list=new_list,
                product=original_item.product,
                sku=original_item.sku,
                product_type=original_item.product_type,
                product_name=original_item.product_name,
                sku_code=original_item.sku_code,
                quantity=remaining,
                unit=original_item.unit,
                unit_price=original_item.unit_price,
                supplier=original_item.supplier,
                location=original_item.location,
                quality_level=original_item.quality_level,
                material=original_item.material,
                size=original_item.size,
                color=original_item.color,
                remark=original_item.remark,
                purchased_quantity=Decimal('0'),
                status=PurchaseItemStatus.PENDING,
            )

        # 重新获取以包含 items
        new_list = PurchaseList.objects.get(id=new_list.id)
        return JsonResponse({
            'purchase_list': purchase_list_to_dict(new_list, include_items=True),
            'item': purchase_item_to_dict(new_item),
        }, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
