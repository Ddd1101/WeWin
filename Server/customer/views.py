from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Q
import json
import jwt
from django.conf import settings
from decimal import Decimal
from account.models import User, UserType
from company.models import Company
from store.models import Product
from .models import Customer, CustomerVisibility, CustomerProduct, CustomerPriceHistory


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


def get_visible_customers(current_user):
    """
    根据用户类型返回可见的客户查询集
    - 企业负责人看所有
    - 管理员看自己创建和授权的
    - 普通用户看授权的
    """
    if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
        return Customer.objects.all()
    elif current_user.user_type == UserType.ENTERPRISE_LEADER:
        if current_user.company:
            return Customer.objects.filter(company=current_user.company)
        return Customer.objects.none()
    elif current_user.user_type == UserType.ENTERPRISE_ADMIN:
        if current_user.company:
            # 管理员看自己创建和授权的
            created_customers = Customer.objects.filter(
                company=current_user.company,
                created_by=current_user
            )
            authorized_customers = Customer.objects.filter(
                company=current_user.company,
                visibilities__visible_user=current_user
            )
            return (created_customers | authorized_customers).distinct()
        return Customer.objects.none()
    elif current_user.user_type == UserType.ENTERPRISE_USER:
        if current_user.company:
            # 普通用户看授权的
            return Customer.objects.filter(
                company=current_user.company,
                visibilities__visible_user=current_user
            )
        return Customer.objects.none()
    return Customer.objects.none()


def check_customer_permission(current_user, customer):
    """
    检查用户是否有权限操作某个客户
    """
    if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
        return True
    if current_user.user_type == UserType.ENTERPRISE_LEADER:
        return current_user.company == customer.company
    if current_user.user_type == UserType.ENTERPRISE_ADMIN:
        if current_user.company != customer.company:
            return False
        return customer.created_by == current_user or \
               customer.visibilities.filter(visible_user=current_user).exists()
    if current_user.user_type == UserType.ENTERPRISE_USER:
        return current_user.company == customer.company and \
               customer.visibilities.filter(visible_user=current_user).exists()
    return False


def customer_to_dict(customer):
    """将客户对象转换为字典"""
    return {
        'id': customer.id,
        'name': customer.name,
        'phone': customer.phone,
        'email': customer.email,
        'address': customer.address,
        'company_id': customer.company_id,
        'company_name': customer.company.name,
        'contact_name': customer.contact_name,
        'remark': customer.remark,
        'is_active': customer.is_active,
        'created_by_id': customer.created_by_id,
        'created_by_name': customer.created_by.username if customer.created_by else None,
        'created_at': customer.created_at.isoformat(),
        'updated_at': customer.updated_at.isoformat()
    }


@require_http_methods(['GET'])
def get_customers(request):
    """获取客户列表"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customers = get_visible_customers(current_user)

        # 筛选条件
        is_active = request.GET.get('is_active')
        if is_active is not None:
            customers = customers.filter(is_active=is_active == 'true')

        # 搜索
        search = request.GET.get('search')
        if search:
            customers = customers.filter(
                Q(name__icontains=search) |
                Q(phone__icontains=search) |
                Q(contact_name__icontains=search)
            )

        # 分页
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        offset = (page - 1) * page_size

        total_count = customers.count()
        customers = customers.order_by('-created_at')[offset:offset + page_size]

        customer_list = [customer_to_dict(customer) for customer in customers]

        return JsonResponse({
            'customers': customer_list,
            'total_count': total_count,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_customer(request):
    """创建客户"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if current_user.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限创建客户'}, status=403)

        data = json.loads(request.body)
        name = data.get('name')
        company_id = data.get('company_id')

        if not name:
            return JsonResponse({'error': '客户名称不能为空'}, status=400)

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
            customer = Customer.objects.create(
                name=name,
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address'),
                company=company,
                contact_name=data.get('contact_name'),
                remark=data.get('remark'),
                is_active=data.get('is_active', True),
                created_by=current_user
            )

            # 如果指定了可见用户，创建可见性配置
            visible_user_ids = data.get('visible_user_ids', [])
            if visible_user_ids:
                for user_id in visible_user_ids:
                    try:
                        visible_user = User.objects.get(id=user_id, company=company)
                        CustomerVisibility.objects.create(
                            customer=customer,
                            visible_user=visible_user,
                            configured_by=current_user
                        )
                    except User.DoesNotExist:
                        continue

        return JsonResponse(customer_to_dict(customer), status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['PUT'])
def update_customer(request, customer_id):
    """更新客户"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customer = Customer.objects.get(id=customer_id)

        if not check_customer_permission(current_user, customer):
            return JsonResponse({'error': '无权限更新客户'}, status=403)

        data = json.loads(request.body)

        if 'name' in data:
            customer.name = data['name']
        if 'phone' in data:
            customer.phone = data['phone']
        if 'email' in data:
            customer.email = data['email']
        if 'address' in data:
            customer.address = data['address']
        if 'contact_name' in data:
            customer.contact_name = data['contact_name']
        if 'remark' in data:
            customer.remark = data['remark']
        if 'is_active' in data:
            customer.is_active = data['is_active']

        customer.save()

        return JsonResponse(customer_to_dict(customer))
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Customer.DoesNotExist:
        return JsonResponse({'error': '客户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['DELETE'])
def delete_customer(request, customer_id):
    """删除客户"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customer = Customer.objects.get(id=customer_id)

        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type == UserType.ENTERPRISE_LEADER:
            if current_user.company == customer.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限删除客户'}, status=403)

        customer.delete()
        return JsonResponse({'message': '客户删除成功'})
    except Customer.DoesNotExist:
        return JsonResponse({'error': '客户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_customer_detail(request, customer_id):
    """获取客户详情"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customer = Customer.objects.get(id=customer_id)

        if not check_customer_permission(current_user, customer):
            return JsonResponse({'error': '无权限查看客户详情'}, status=403)

        # 获取可见用户列表
        visible_users = []
        for visibility in customer.visibilities.select_related('visible_user').all():
            visible_users.append({
                'id': visibility.visible_user.id,
                'username': visibility.visible_user.username,
                'real_name': visibility.visible_user.real_name,
                'configured_at': visibility.configured_at.isoformat()
            })

        result = customer_to_dict(customer)
        result['visible_users'] = visible_users

        return JsonResponse(result)
    except Customer.DoesNotExist:
        return JsonResponse({'error': '客户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_customer_products(request, customer_id):
    """获取客户商品关联列表"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customer = Customer.objects.get(id=customer_id)

        if not check_customer_permission(current_user, customer):
            return JsonResponse({'error': '无权限查看客户商品'}, status=403)

        customer_products = customer.products.select_related('product').all()

        product_list = []
        for cp in customer_products:
            product_list.append({
                'id': cp.id,
                'customer_id': cp.customer_id,
                'product_id': cp.product_id,
                'product_code': cp.product.code,
                'product_name': cp.product.name,
                'product_type': cp.product.product_type,
                'product_type_display': cp.product.get_product_type_display(),
                'price': float(cp.price),
                'is_active': cp.is_active,
                'created_at': cp.created_at.isoformat(),
                'updated_at': cp.updated_at.isoformat()
            })

        return JsonResponse({'customer_products': product_list})
    except Customer.DoesNotExist:
        return JsonResponse({'error': '客户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_or_update_customer_product(request, customer_id):
    """创建或更新客户商品关联"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customer = Customer.objects.get(id=customer_id)

        if not check_customer_permission(current_user, customer):
            return JsonResponse({'error': '无权限操作客户商品'}, status=403)

        data = json.loads(request.body)
        product_id = data.get('product_id')
        price = data.get('price')
        is_active = data.get('is_active', True)

        if not product_id or price is None:
            return JsonResponse({'error': '商品ID和价格不能为空'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'error': '商品不存在'}, status=404)

        with transaction.atomic():
            customer_product, created = CustomerProduct.objects.get_or_create(
                customer=customer,
                product=product,
                defaults={
                    'price': Decimal(str(price)),
                    'is_active': is_active
                }
            )

            if not created:
                old_price = customer_product.price
                customer_product.price = Decimal(str(price))
                customer_product.is_active = is_active
                customer_product.save()

                # 记录价格历史
                if old_price != Decimal(str(price)):
                    CustomerPriceHistory.objects.create(
                        customer=customer,
                        product=product,
                        price=Decimal(str(price)),
                        created_by=current_user
                    )
            else:
                # 新创建的也记录历史
                CustomerPriceHistory.objects.create(
                    customer=customer,
                    product=product,
                    price=Decimal(str(price)),
                    created_by=current_user
                )

        return JsonResponse({
            'id': customer_product.id,
            'customer_id': customer_product.customer_id,
            'product_id': customer_product.product_id,
            'product_code': customer_product.product.code,
            'product_name': customer_product.product.name,
            'price': float(customer_product.price),
            'is_active': customer_product.is_active,
            'created': created,
            'created_at': customer_product.created_at.isoformat(),
            'updated_at': customer_product.updated_at.isoformat()
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Customer.DoesNotExist:
        return JsonResponse({'error': '客户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_customer_price_history(request, customer_id, product_id):
    """获取客户商品报价历史"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customer = Customer.objects.get(id=customer_id)

        if not check_customer_permission(current_user, customer):
            return JsonResponse({'error': '无权限查看报价历史'}, status=403)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'error': '商品不存在'}, status=404)

        price_histories = CustomerPriceHistory.objects.filter(
            customer=customer,
            product=product
        ).select_related('created_by').order_by('-created_at')

        history_list = []
        for history in price_histories:
            history_list.append({
                'id': history.id,
                'customer_id': history.customer_id,
                'product_id': history.product_id,
                'price': float(history.price),
                'created_by_id': history.created_by_id,
                'created_by_name': history.created_by.username if history.created_by else None,
                'created_at': history.created_at.isoformat()
            })

        return JsonResponse({'price_histories': history_list})
    except Customer.DoesNotExist:
        return JsonResponse({'error': '客户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_customer_visibility(request, customer_id):
    """获取客户可见性配置"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customer = Customer.objects.get(id=customer_id)

        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if current_user.company == customer.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限查看可见性配置'}, status=403)

        visibilities = customer.visibilities.select_related('visible_user', 'configured_by').all()

        visibility_list = []
        for visibility in visibilities:
            visibility_list.append({
                'id': visibility.id,
                'customer_id': visibility.customer_id,
                'visible_user_id': visibility.visible_user_id,
                'visible_user_username': visibility.visible_user.username,
                'visible_user_real_name': visibility.visible_user.real_name,
                'configured_by_id': visibility.configured_by_id,
                'configured_by_name': visibility.configured_by.username if visibility.configured_by else None,
                'configured_at': visibility.configured_at.isoformat()
            })

        return JsonResponse({'visibilities': visibility_list})
    except Customer.DoesNotExist:
        return JsonResponse({'error': '客户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def set_customer_visibility(request, customer_id):
    """设置客户可见性"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customer = Customer.objects.get(id=customer_id)

        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if current_user.company == customer.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限配置可见性'}, status=403)

        data = json.loads(request.body)
        user_ids = data.get('user_ids', [])

        with transaction.atomic():
            # 删除所有现有配置
            customer.visibilities.all().delete()

            # 添加新配置
            for user_id in user_ids:
                try:
                    visible_user = User.objects.get(id=user_id, company=customer.company)
                    CustomerVisibility.objects.create(
                        customer=customer,
                        visible_user=visible_user,
                        configured_by=current_user
                    )
                except User.DoesNotExist:
                    continue

        # 返回更新后的配置
        visibilities = customer.visibilities.select_related('visible_user', 'configured_by').all()

        visibility_list = []
        for visibility in visibilities:
            visibility_list.append({
                'id': visibility.id,
                'customer_id': visibility.customer_id,
                'visible_user_id': visibility.visible_user_id,
                'visible_user_username': visibility.visible_user.username,
                'visible_user_real_name': visibility.visible_user.real_name,
                'configured_by_id': visibility.configured_by_id,
                'configured_by_name': visibility.configured_by.username if visibility.configured_by else None,
                'configured_at': visibility.configured_at.isoformat()
            })

        return JsonResponse({'visibilities': visibility_list})
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Customer.DoesNotExist:
        return JsonResponse({'error': '客户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['DELETE'])
def delete_customer_product(request, customer_id, customer_product_id):
    """删除客户商品关联"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        customer = Customer.objects.get(id=customer_id)

        if not check_customer_permission(current_user, customer):
            return JsonResponse({'error': '无权限操作客户商品'}, status=403)

        customer_product = CustomerProduct.objects.get(id=customer_product_id, customer=customer)
        customer_product.delete()

        return JsonResponse({'message': '客户商品关联删除成功'})
    except Customer.DoesNotExist:
        return JsonResponse({'error': '客户不存在'}, status=404)
    except CustomerProduct.DoesNotExist:
        return JsonResponse({'error': '客户商品关联不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['DELETE'])
def remove_customer_visibility(request, customer_id, visibility_id):
    """删除客户可见性配置"""
    try:
        current_user, error_response = authenticate_jwt(request)
        if error_response:
            return error_response

        visibility = CustomerVisibility.objects.get(id=visibility_id, customer_id=customer_id)

        has_permission = False
        if current_user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif current_user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if current_user.company == visibility.customer.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限删除可见性配置'}, status=403)

        visibility.delete()
        return JsonResponse({'message': '可见性配置删除成功'})
    except CustomerVisibility.DoesNotExist:
        return JsonResponse({'error': '可见性配置不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
