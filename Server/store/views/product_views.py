from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
import traceback
from datetime import datetime, timedelta
from decimal import Decimal

from account.models import User, UserType
from company.models import Company
from store.models import Product, ProductType, ProductSku, Bead, Accessory, FinishedProduct, FinishedProductBead, FinishedProductAccessory, ChildrenClothing
from .helpers import calculate_finished_product_cost, sku_to_dict, get_default_sku, ensure_default_sku, sync_skus, sku_schema_ready, product_skus_payload
from utils.decorators import jwt_required


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
@jwt_required
def get_product_stats(request):
    try:
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            products = Product.objects.all()
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
            products = Product.objects.filter(company=request.user.company) if request.user.company else Product.objects.none()
        else:
            products = Product.objects.none()

        active_products = products.filter(is_active=True)
        stats = {
            'total_count': products.count(),
            'active_count': active_products.count(),
            'bead_count': products.filter(product_type=ProductType.BEAD).count(),
            'accessory_count': products.filter(product_type=ProductType.ACCESSORY).count(),
            'finished_count': products.filter(product_type=ProductType.FINISHED).count(),
            'children_clothing_count': products.filter(product_type=ProductType.CHILDREN_CLOTHING).count(),
            'sku_count': ProductSku.objects.filter(product__in=products).count() if sku_schema_ready() else 0,
        }
        return JsonResponse({'product_stats': stats})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
@jwt_required
def get_products(request):
    try:
        
        products = []
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            products = Product.objects.all()
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
            if request.user.company:
                products = Product.objects.filter(company=request.user.company)

        # 筛选条件
        product_type = request.GET.get('product_type')
        if product_type:
            products = products.filter(product_type=product_type)

        is_active = request.GET.get('is_active')
        if is_active is not None:
            products = products.filter(is_active=is_active == 'true')

        # 排序
        ordering = request.GET.get('ordering', '')
        if ordering in ('code', '-code'):
            products = products.order_by(ordering)
        elif ordering:
            products = products.order_by(ordering)

        # 分页
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 50))
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
                'purchase_cost': float(product.purchase_cost),
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
                    product_data['skus'] = product_skus_payload(product)
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
                    product_data['skus'] = product_skus_payload(product)
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
                    # 计算总成本
                    total_cost = Decimal('0')
                    # 获取成品的串珠组成
                    for fpb in FinishedProductBead.objects.select_related('bead__product', 'sku').filter(finished_product=finished):
                        bead_product = fpb.bead.product
                        bead = fpb.bead
                        sku = fpb.sku if fpb.sku_id else get_default_sku(bead_product)
                        sku_payload = sku_to_dict(sku) if sku else None
                        bead_cost_price = sku.cost_price if sku else bead_product.cost_price
                        bead_purchase_cost = sku.purchase_cost if sku else bead_product.purchase_cost
                        total_cost += bead_cost_price * fpb.quantity
                        product_data['finished']['beads'].append({
                            'bead_id': bead_product.id,
                            'sku_id': sku.id if sku else None,
                            'sku': sku_payload,
                            'bead_code': bead_product.code,
                            'bead_name': bead_product.name,
                            'bead_cost_price': float(bead_cost_price),
                            'bead_purchase_cost': float(bead_purchase_cost) if bead_purchase_cost else None,
                            'bead_image_url': request.build_absolute_uri(bead_product.image.url) if bead_product.image else None,
                            'quantity': fpb.quantity,
                            'bead_weight': float(sku.weight if sku else bead.weight),
                            'bead_quality_level': sku.quality_level if sku else bead.quality_level,
                            'bead_remark': sku.remark if sku else bead.remark,
                            'bead_size': sku.size if sku else bead.size
                        })
                    # 获取成品的配件组成
                    for fpa in FinishedProductAccessory.objects.select_related('accessory__product', 'sku').filter(finished_product=finished):
                        acc_product = fpa.accessory.product
                        sku = fpa.sku if fpa.sku_id else get_default_sku(acc_product)
                        sku_payload = sku_to_dict(sku) if sku else None
                        accessory_cost_price = sku.cost_price if sku else acc_product.cost_price
                        total_cost += accessory_cost_price * fpa.quantity
                        product_data['finished']['accessories'].append({
                            'accessory_id': acc_product.id,
                            'sku_id': sku.id if sku else None,
                            'sku': sku_payload,
                            'accessory_code': acc_product.code,
                            'accessory_name': acc_product.name,
                            'accessory_cost_price': float(accessory_cost_price),
                            'accessory_image_url': request.build_absolute_uri(acc_product.image.url) if acc_product.image else None,
                            'quantity': fpa.quantity
                        })
                    # 加上工费和弹性成本
                    total_cost += finished.labor_cost
                    total_cost += finished.elastic_cost
                    product_data['cost_price'] = float(total_cost)
                except FinishedProduct.DoesNotExist:
                    pass
            elif product.product_type == ProductType.CHILDREN_CLOTHING:
                try:
                    cc = ChildrenClothing.objects.get(product=product)
                    product_data['children_clothing'] = {
                        'fabric': cc.fabric,
                        'size': cc.size,
                        'color': cc.color,
                        'season': cc.season,
                        'gender': cc.gender,
                        'age_range': cc.age_range,
                    }
                except ChildrenClothing.DoesNotExist:
                    pass
                product_data['skus'] = product_skus_payload(product)

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
@jwt_required
def create_product(request):
    try:
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if request.user.company:
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
            if 'skus' in request.POST:
                try:
                    data_dict['skus'] = json.loads(request.POST['skus'])
                except (json.JSONDecodeError, TypeError):
                    data_dict['skus'] = []
            image = request.FILES.get('image')
        else:
            data_dict = json.loads(request.body)
            image = None

        # 辅助函数：安全转换为 Decimal
        def to_decimal(value, default=0):
            if value is None or value == '':
                return Decimal(str(default))
            try:
                return Decimal(str(value))
            except (ValueError, TypeError):
                return Decimal(str(default))

        # 辅助函数：安全转换为整数
        def to_integer(value, default=None):
            if value is None or value == '':
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # 辅助函数：安全转换为布尔值
        def to_boolean(value, default=False):
            if isinstance(value, bool):
                return value
            if value is None or value == '':
                return default
            return str(value).lower() in ['true', '1', 'yes', 'on']

        code = data_dict.get('code')
        name = data_dict.get('name')
        product_type = data_dict.get('product_type')
        purchase_cost = to_decimal(data_dict.get('purchase_cost', 0))
        cost_price = to_decimal(data_dict.get('cost_price', 0))
        selling_price = to_decimal(data_dict.get('selling_price', 0))
        location = data_dict.get('location', '')
        supplier = data_dict.get('supplier', '')
        company_id = data_dict.get('company_id')
        is_active = to_boolean(data_dict.get('is_active', True))

        if not all([code, name, product_type]):
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

        # 检查货号是否已存在
        if Product.objects.filter(code=code, company=company).exists():
            return JsonResponse({'error': '货号已存在'}, status=400)

        with transaction.atomic():
            # 计算单颗成本（仅对串珠有效）
            if product_type == ProductType.BEAD:
                weight = to_decimal(data_dict.get('weight', 0))
                cost_price = purchase_cost * weight
            else:
                # 配件和成品直接使用传入的 cost_price
                cost_price = to_decimal(data_dict.get('cost_price', 0))
            
            product = Product.objects.create(
                code=code,
                name=name,
                product_type=product_type,
                purchase_cost=purchase_cost,
                cost_price=cost_price,
                selling_price=selling_price,
                location=location,
                supplier=supplier,
                company=company,
                image=image,
                is_active=is_active,
                created_by=request.user
            )

            # 创建串珠、配件或成品
            if product_type == ProductType.BEAD:
                size_value = to_integer(data_dict.get('size'))
                bead = Bead.objects.create(
                    product=product,
                    material=data_dict.get('material', ''),
                    size=size_value,
                    color=data_dict.get('color', ''),
                    weight=to_decimal(data_dict.get('weight', 0)),
                    quality_level=to_integer(data_dict.get('quality_level', 5)),
                    remark=data_dict.get('remark', '')
                )
                if sku_schema_ready():
                    sync_skus(product, data_dict.get('skus') or [{
                        'sku_code': f'{code}-默认', 'name': '默认SKU', 'material': bead.material,
                        'size': bead.size, 'color': bead.color, 'purchase_cost': product.purchase_cost,
                        'cost_price': product.cost_price, 'weight': bead.weight,
                        'quality_level': bead.quality_level, 'remark': bead.remark, 'is_default': True
                    }], to_decimal, to_integer, bead)
            elif product_type == ProductType.ACCESSORY:
                size_value = to_integer(data_dict.get('size'))
                accessory = Accessory.objects.create(
                    product=product,
                    material=data_dict.get('material', ''),
                    size=size_value,
                    color=data_dict.get('color', '')
                )
                if sku_schema_ready():
                    sync_skus(product, data_dict.get('skus') or [{
                        'sku_code': f'{code}-默认', 'name': '默认SKU', 'material': accessory.material,
                        'size': accessory.size, 'color': accessory.color, 'purchase_cost': product.purchase_cost,
                        'cost_price': product.cost_price, 'is_default': True
                    }], to_decimal, to_integer, accessory)
            elif product_type == ProductType.FINISHED:
                finished = FinishedProduct.objects.create(
                    product=product,
                    labor_cost=to_decimal(data_dict.get('labor_cost', 0)),
                    elastic_cost=to_decimal(data_dict.get('elastic_cost', 0))
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
                        if sku_schema_ready():
                            sku = ProductSku.objects.filter(id=bead_data.get('sku_id'), product=bead_product).first() or ensure_default_sku(bead_product, bead)
                            FinishedProductBead.objects.create(
                                finished_product=finished, bead=bead, sku=sku,
                                quantity=to_integer(bead_data['quantity'], 1)
                            )
                        else:
                            FinishedProductBead.objects.create(
                                finished_product=finished, bead=bead,
                                quantity=to_integer(bead_data['quantity'], 1)
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
                        if sku_schema_ready():
                            sku = ProductSku.objects.filter(id=acc.get('sku_id'), product=accessory_product).first() or ensure_default_sku(accessory_product, accessory)
                            FinishedProductAccessory.objects.create(
                                finished_product=finished, accessory=accessory, sku=sku,
                                quantity=to_integer(acc['quantity'], 1)
                            )
                        else:
                            FinishedProductAccessory.objects.create(
                                finished_product=finished, accessory=accessory,
                                quantity=to_integer(acc['quantity'], 1)
                            )
                    except (Product.DoesNotExist, Accessory.DoesNotExist):
                        pass
                
                # 重新计算并保存成品的成本价格
                product.cost_price = calculate_finished_product_cost(finished)
                product.save()
            elif product_type == ProductType.CHILDREN_CLOTHING:
                ChildrenClothing.objects.create(
                    product=product,
                    fabric=data_dict.get('fabric', ''),
                    size=data_dict.get('size', ''),
                    color=data_dict.get('color', ''),
                    season=data_dict.get('season', ''),
                    gender=data_dict.get('gender', ''),
                    age_range=data_dict.get('age_range', ''),
                )

        # 构建响应数据
        product_data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'product_type': product.product_type,
            'product_type_display': product.get_product_type_display(),
            'purchase_cost': float(product.purchase_cost),
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
@jwt_required
def update_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN]:
            if request.user.company == product.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限更新商品'}, status=403)

        # 支持 multipart/form-data 和 application/json 两种格式
        # 注意：Django 只对 POST 请求自动解析 multipart 数据，PUT 请求需手动解析
        data_dict = {}
        image = None
        remove_image = False
        remove_image_val = False

        if request.content_type and 'multipart/form-data' in request.content_type:
            # PUT 请求时手动解析 multipart 数据
            # Django 只对 POST 请求自动解析 multipart，PUT 需用 MultiPartParser 手动解析
            if request.method == 'PUT':
                from django.http.multipartparser import MultiPartParser
                parser = MultiPartParser(
                    request.META, request, request.upload_handlers, request.encoding
                )
                post_dict, files_dict = parser.parse()
            else:
                post_dict = request.POST
                files_dict = request.FILES

            # 从 POST 中获取普通字段数据
            for key in post_dict:
                data_dict[key] = post_dict[key]
            # 处理 JSON 字段，特别是 beads 和 accessories
            if 'beads' in post_dict:
                try:
                    data_dict['beads'] = json.loads(post_dict['beads'])
                except (json.JSONDecodeError, TypeError):
                    data_dict['beads'] = []
            if 'accessories' in post_dict:
                try:
                    data_dict['accessories'] = json.loads(post_dict['accessories'])
                except (json.JSONDecodeError, TypeError):
                    data_dict['accessories'] = []
            if 'skus' in post_dict:
                try:
                    data_dict['skus'] = json.loads(post_dict['skus'])
                except (json.JSONDecodeError, TypeError):
                    data_dict['skus'] = []
            image = files_dict.get('image')
            remove_image_val = post_dict.get('remove_image', 'false').lower() == 'true'
        else:
            data_dict = json.loads(request.body)
            image = None
            remove_image = data_dict.get('remove_image', False)

        # 辅助函数：安全转换为 Decimal
        def to_decimal(value, default=0):
            if value is None or value == '':
                return Decimal(str(default))
            try:
                return Decimal(str(value))
            except (ValueError, TypeError):
                return Decimal(str(default))

        # 辅助函数：安全转换为整数
        def to_integer(value, default=None):
            if value is None or value == '':
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # 辅助函数：安全转换为布尔值
        def to_boolean(value, default=False):
            if isinstance(value, bool):
                return value
            if value is None or value == '':
                return default
            return str(value).lower() in ['true', '1', 'yes', 'on']

        # 更新商品基本信息
        if 'name' in data_dict:
            product.name = data_dict['name']

        if 'purchase_cost' in data_dict:
            product.purchase_cost = to_decimal(data_dict['purchase_cost'])

        if 'cost_price' in data_dict:
            # 对串珠不直接更新 cost_price，会在后面根据 weight 和 purchase_cost 计算
            if product.product_type != ProductType.BEAD:
                product.cost_price = to_decimal(data_dict['cost_price'])

        if 'selling_price' in data_dict:
            product.selling_price = to_decimal(data_dict['selling_price'])

        if 'location' in data_dict:
            product.location = data_dict['location']

        if 'supplier' in data_dict:
            product.supplier = data_dict['supplier']

        if 'is_active' in data_dict:
            product.is_active = to_boolean(data_dict['is_active'])

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
                    size_value = to_integer(data_dict['size'])
                    bead.size = size_value
                if 'color' in data_dict:
                    bead.color = data_dict['color']
                if 'weight' in data_dict:
                    bead.weight = to_decimal(data_dict['weight'])
                if 'quality_level' in data_dict:
                    bead.quality_level = to_integer(data_dict['quality_level'])
                if 'remark' in data_dict:
                    bead.remark = data_dict['remark']
                bead.save()
                if sku_schema_ready():
                    sync_skus(product, data_dict.get('skus') or [{
                        'sku_code': f'{product.code}-默认', 'name': '默认SKU', 'material': bead.material,
                        'size': bead.size, 'color': bead.color, 'purchase_cost': product.purchase_cost,
                        'cost_price': product.purchase_cost * bead.weight, 'weight': bead.weight,
                        'quality_level': bead.quality_level, 'remark': bead.remark, 'is_default': True
                    }], to_decimal, to_integer, bead)
                
                # 重新计算单颗成本
                weight = bead.weight
                product.cost_price = product.purchase_cost * weight
                product.save()
            except Bead.DoesNotExist:
                pass
        elif product.product_type == ProductType.ACCESSORY:
            try:
                accessory = Accessory.objects.get(product=product)
                if 'material' in data_dict:
                    accessory.material = data_dict['material']
                if 'size' in data_dict:
                    size_value = to_integer(data_dict['size'])
                    accessory.size = size_value
                if 'color' in data_dict:
                    accessory.color = data_dict['color']
                accessory.save()
                if sku_schema_ready():
                    sync_skus(product, data_dict.get('skus') or [{
                        'sku_code': f'{product.code}-默认', 'name': '默认SKU', 'material': accessory.material,
                        'size': accessory.size, 'color': accessory.color, 'purchase_cost': product.purchase_cost,
                        'cost_price': product.cost_price, 'is_default': True
                    }], to_decimal, to_integer, accessory)
            except Accessory.DoesNotExist:
                pass
        elif product.product_type == ProductType.FINISHED:
            try:
                finished = FinishedProduct.objects.get(product=product)
                # 更新工费和弹性成本
                if 'labor_cost' in data_dict:
                    finished.labor_cost = to_decimal(data_dict['labor_cost'])
                if 'elastic_cost' in data_dict:
                    finished.elastic_cost = to_decimal(data_dict['elastic_cost'])
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
                            if sku_schema_ready():
                                sku = ProductSku.objects.filter(id=bead_data.get('sku_id'), product=bead_product).first() or ensure_default_sku(bead_product, bead)
                                FinishedProductBead.objects.create(
                                    finished_product=finished,
                                    bead=bead,
                                    sku=sku,
                                    quantity=to_integer(bead_data['quantity'], 1)
                                )
                            else:
                                FinishedProductBead.objects.create(
                                    finished_product=finished,
                                    bead=bead,
                                    quantity=to_integer(bead_data['quantity'], 1)
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
                            if sku_schema_ready():
                                sku = ProductSku.objects.filter(id=acc.get('sku_id'), product=accessory_product).first() or ensure_default_sku(accessory_product, accessory)
                                FinishedProductAccessory.objects.create(
                                    finished_product=finished,
                                    accessory=accessory,
                                    sku=sku,
                                    quantity=to_integer(acc['quantity'], 1)
                                )
                            else:
                                FinishedProductAccessory.objects.create(
                                    finished_product=finished,
                                    accessory=accessory,
                                    quantity=to_integer(acc['quantity'], 1)
                                )
                        except (Product.DoesNotExist, Accessory.DoesNotExist):
                            pass
                
                # 重新计算并保存成品的成本价格
                product.cost_price = calculate_finished_product_cost(finished)
                product.save()
            except FinishedProduct.DoesNotExist:
                pass
        elif product.product_type == ProductType.CHILDREN_CLOTHING:
            try:
                cc = ChildrenClothing.objects.get(product=product)
                if 'fabric' in data_dict:
                    cc.fabric = data_dict['fabric']
                if 'size' in data_dict:
                    cc.size = data_dict['size']
                if 'color' in data_dict:
                    cc.color = data_dict['color']
                if 'season' in data_dict:
                    cc.season = data_dict['season']
                if 'gender' in data_dict:
                    cc.gender = data_dict['gender']
                if 'age_range' in data_dict:
                    cc.age_range = data_dict['age_range']
                cc.save()
            except ChildrenClothing.DoesNotExist:
                pass

        # 构建响应数据
        product_data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'product_type': product.product_type,
            'product_type_display': product.get_product_type_display(),
            'purchase_cost': float(product.purchase_cost),
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
        traceback.print_exc()
        return JsonResponse({'error': str(e), 'trace': traceback.format_exc()[-2000:]}, status=500)


@csrf_exempt
@require_http_methods(['DELETE'])
@jwt_required
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type == UserType.ENTERPRISE_LEADER:
            if request.user.company == product.company:
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
@jwt_required
def get_product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        
        has_permission = False
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            has_permission = True
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
            if request.user.company == product.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限查看商品详情'}, status=403)

        product_data = {
            'id': product.id,
            'code': product.code,
            'name': product.name,
            'product_type': product.product_type,
            'product_type_display': product.get_product_type_display(),
            'purchase_cost': float(product.purchase_cost),
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
                product_data['skus'] = product_skus_payload(product)
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
                product_data['skus'] = product_skus_payload(product)
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
                # 计算总成本
                total_cost = Decimal('0')
                # 获取成品的串珠组成
                for fpb in FinishedProductBead.objects.select_related('bead__product', 'sku').filter(finished_product=finished):
                    bead_product = fpb.bead.product
                    bead = fpb.bead
                    sku = fpb.sku if fpb.sku_id else get_default_sku(bead_product)
                    sku_payload = sku_to_dict(sku) if sku else None
                    bead_cost_price = sku.cost_price if sku else bead_product.cost_price
                    bead_purchase_cost = sku.purchase_cost if sku else bead_product.purchase_cost
                    total_cost += bead_cost_price * fpb.quantity
                    product_data['finished']['beads'].append({
                        'bead_id': bead_product.id,
                        'sku_id': sku.id if sku else None,
                        'sku': sku_payload,
                        'bead_code': bead_product.code,
                        'bead_name': bead_product.name,
                        'bead_cost_price': float(bead_cost_price),
                        'bead_purchase_cost': float(bead_purchase_cost) if bead_purchase_cost else None,
                        'bead_image_url': request.build_absolute_uri(bead_product.image.url) if bead_product.image else None,
                        'quantity': fpb.quantity,
                        'bead_weight': float(sku.weight if sku else bead.weight),
                        'bead_quality_level': sku.quality_level if sku else bead.quality_level,
                        'bead_remark': sku.remark if sku else bead.remark,
                        'bead_size': sku.size if sku else bead.size
                    })
                # 获取成品的配件组成
                for fpa in FinishedProductAccessory.objects.select_related('accessory__product', 'sku').filter(finished_product=finished):
                    acc_product = fpa.accessory.product
                    sku = fpa.sku if fpa.sku_id else get_default_sku(acc_product)
                    sku_payload = sku_to_dict(sku) if sku else None
                    accessory_cost_price = sku.cost_price if sku else acc_product.cost_price
                    total_cost += accessory_cost_price * fpa.quantity
                    product_data['finished']['accessories'].append({
                        'accessory_id': acc_product.id,
                        'sku_id': sku.id if sku else None,
                        'sku': sku_payload,
                        'accessory_code': acc_product.code,
                        'accessory_name': acc_product.name,
                        'accessory_cost_price': float(accessory_cost_price),
                        'accessory_image_url': request.build_absolute_uri(acc_product.image.url) if acc_product.image else None,
                        'quantity': fpa.quantity
                    })
                # 加上工费和弹性成本
                total_cost += finished.labor_cost
                total_cost += finished.elastic_cost
                product_data['cost_price'] = float(total_cost)
            except FinishedProduct.DoesNotExist:
                pass
        elif product.product_type == ProductType.CHILDREN_CLOTHING:
            try:
                cc = ChildrenClothing.objects.get(product=product)
                product_data['children_clothing'] = {
                    'fabric': cc.fabric,
                    'size': cc.size,
                    'color': cc.color,
                    'season': cc.season,
                    'gender': cc.gender,
                    'age_range': cc.age_range,
                }
            except ChildrenClothing.DoesNotExist:
                pass
            product_data['skus'] = product_skus_payload(product)

        return JsonResponse(product_data)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({'error': '商品不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
@jwt_required
def get_accessories(request):
    try:
        
        accessories = []
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            accessories = Accessory.objects.all()
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
            if request.user.company:
                accessories = Accessory.objects.filter(product__company=request.user.company)

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
                'color': accessory.color,
                'image_url': request.build_absolute_uri(product.image.url) if product.image else None,
                'skus': product_skus_payload(product)
            })

        return JsonResponse({'accessories': accessory_list})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
@jwt_required
def get_beads(request):
    try:
        
        beads = []
        if request.user.user_type in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            beads = Bead.objects.all()
        elif request.user.user_type in [UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]:
            if request.user.company:
                beads = Bead.objects.filter(product__company=request.user.company)

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
                'remark': bead.remark,
                'image_url': request.build_absolute_uri(product.image.url) if product.image else None,
                'skus': product_skus_payload(product)
            })

        return JsonResponse({'beads': bead_list})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
@jwt_required
def get_product_skus(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        if request.user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN] and request.user.company != product.company:
            return JsonResponse({'error': '无权限查看SKU'}, status=403)
        return JsonResponse({'skus': product_skus_payload(product)})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({'error': '商品不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
@jwt_required
def get_children_clothing_costs(request):
    """返回童装成本矩阵：所有货号的供应商 + 尺码成本"""
    try:
        products = Product.objects.filter(
            product_type=ProductType.CHILDREN_CLOTHING
        )
        if request.user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            products = products.filter(company=request.user.company)
        products = products.prefetch_related('skus')

        all_sizes = set()
        rows = []
        for product in products:
            costs = {}
            for sku in product.skus.all():
                size_key = str(sku.size) if sku.size is not None else (sku.name or '')
                if not size_key:
                    continue
                costs[size_key] = float(sku.cost_price)
                all_sizes.add(size_key)
            rows.append({
                'id': product.id,
                'code': product.code,
                'name': product.name,
                'supplier': product.supplier or '',
                'costs': costs,
            })

        def size_sort_key(s):
            try:
                return (0, int(s), s)
            except (ValueError, TypeError):
                return (1, 0, s)

        columns = sorted(all_sizes, key=size_sort_key)

        return JsonResponse({'columns': columns, 'rows': rows})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
@jwt_required
def save_children_clothing_costs(request):
    """批量保存童装供应商 + 尺码成本"""
    try:
        data = json.loads(request.body)
        rows = data.get('rows', [])

        updated = 0
        with transaction.atomic():
            for row in rows:
                product_qs = Product.objects.filter(
                    id=row.get('id'),
                    product_type=ProductType.CHILDREN_CLOTHING,
                )
                if request.user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
                    product_qs = product_qs.filter(company=request.user.company)
                product = product_qs.first()
                if not product:
                    continue

                if 'supplier' in row:
                    product.supplier = row.get('supplier') or ''
                    product.save(update_fields=['supplier'])

                costs = row.get('costs')
                if costs:
                    sync_children_clothing_skus(product, costs)

                updated += 1

        return JsonResponse({'message': '保存成功', 'updated': updated})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def sync_children_clothing_skus(product, costs):
    """同步童装 SKU 尺码成本：costs = {尺码字符串: 成本}"""
    kept_ids = set()
    for size_key, cost in costs.items():
        size_key = str(size_key)
        try:
            cost_val = float(cost) if cost not in (None, '') else 0
        except (ValueError, TypeError):
            cost_val = 0

        if size_key.isdigit():
            sku = product.skus.filter(size=int(size_key)).first()
        else:
            sku = product.skus.filter(name=size_key, size__isnull=True).first()

        if sku is None:
            sku = ProductSku(product=product)

        if size_key.isdigit():
            sku.size = int(size_key)
            sku.name = size_key
        else:
            sku.size = None
            sku.name = size_key

        sku.sku_code = f'{product.code}-{size_key}'
        sku.cost_price = cost_val
        sku.selling_price = 0
        sku.is_active = True
        sku.save()
        kept_ids.add(sku.id)

    # 删除已不存在的尺码
    product.skus.exclude(id__in=kept_ids).delete()

    # 确保有默认 SKU
    if not product.skus.filter(is_default=True).exists():
        first = product.skus.filter(is_active=True).order_by('id').first()
        if first:
            first.is_default = True
            first.save(update_fields=['is_default'])

    # 商品级成本 = 最小尺码成本
    valid_costs = [float(c) for c in costs.values() if c not in (None, '')]
    if valid_costs:
        product.cost_price = min(valid_costs)
        product.save(update_fields=['cost_price'])
