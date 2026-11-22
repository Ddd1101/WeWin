from decimal import Decimal
from store.models import ProductSku, ProductType


def calculate_finished_product_cost(finished):
    """
    计算成品的总成本
    公式：串珠成本 + 配件成本 + 工费 + 弹性成本
    """
    total_cost = Decimal('0')
    
    # 计算串珠成本（优先使用SKU成本）
    for fpb in finished.beads.all():
        if fpb.sku_id and fpb.sku:
            total_cost += fpb.sku.cost_price * fpb.quantity
        else:
            total_cost += fpb.bead.product.cost_price * fpb.quantity
    
    # 计算配件成本（优先使用SKU成本）
    for fpa in finished.accessories.all():
        if fpa.sku_id and fpa.sku:
            total_cost += fpa.sku.cost_price * fpa.quantity
        else:
            total_cost += fpa.accessory.product.cost_price * fpa.quantity
    
    # 加上工费和弹性成本
    total_cost += finished.labor_cost
    total_cost += finished.elastic_cost
    
    return total_cost


def sku_to_dict(sku):
    return {
        'id': sku.id,
        'sku_id': sku.id,
        'sku_code': sku.sku_code,
        'sku_name': sku.name,
        'name': sku.name,
        'material': sku.material,
        'size': sku.size,
        'color': sku.color,
        'purchase_cost': float(sku.purchase_cost),
        'cost_price': float(sku.cost_price),
        'weight': float(sku.weight),
        'quality_level': sku.quality_level,
        'selling_price': float(getattr(sku, 'selling_price', 0)),
        'location': getattr(sku, 'location', None),
        'supplier': getattr(sku, 'supplier', None),
        'remark': sku.remark,
        'is_default': sku.is_default,
        'is_active': sku.is_active,
    }


def get_default_sku(product):
    return product.skus.filter(is_active=True, is_default=True).first() or product.skus.filter(is_active=True).first()


def ensure_default_sku(product, detail_obj=None):
    sku = get_default_sku(product)
    if sku:
        return sku
    defaults = {
        'sku_code': f'{product.code}-默认',
        'name': '默认SKU',
        'purchase_cost': product.purchase_cost,
        'cost_price': product.cost_price,
        'is_default': True,
        'is_active': True,
    }
    if detail_obj:
        for attr in ['material', 'size', 'color', 'weight', 'quality_level', 'remark']:
            if hasattr(detail_obj, attr):
                defaults[attr] = getattr(detail_obj, attr)
    return ProductSku.objects.create(product=product, **defaults)


def sync_skus(product, sku_items, to_decimal, to_integer, fallback_detail=None):
    if sku_items is None:
        return
    existing_ids = set(product.skus.values_list('id', flat=True))
    kept_ids = set()
    first_active = None
    default_sku = None
    for idx, item in enumerate(sku_items):
        sku_id = item.get('id') or item.get('sku_id')
        sku = None
        if sku_id:
            try:
                sku = ProductSku.objects.get(id=sku_id, product=product)
            except ProductSku.DoesNotExist:
                sku = None
        if sku is None:
            sku = ProductSku(product=product)
        sku.sku_code = item.get('sku_code') or item.get('code') or sku.sku_code or f'{product.code}-SKU{idx + 1}'
        sku.name = item.get('sku_name') or item.get('name') or sku.name or f'SKU{idx + 1}'
        sku.material = item.get('material', '')
        sku.size = to_integer(item.get('size'))
        sku.color = item.get('color', '')
        sku.purchase_cost = to_decimal(item.get('purchase_cost', product.purchase_cost))
        sku.weight = to_decimal(item.get('weight', 0))
        if product.product_type == ProductType.BEAD and (not item.get('cost_price')):
            sku.cost_price = sku.purchase_cost * sku.weight
        else:
            sku.cost_price = to_decimal(item.get('cost_price', 0))
        sku.quality_level = to_integer(item.get('quality_level', 5), 5)
        sku.selling_price = to_decimal(item.get('selling_price', product.selling_price))
        sku.location = item.get('location', product.location or '')
        sku.supplier = item.get('supplier', product.supplier or '')
        sku.remark = item.get('remark', '')
        sku.is_default = bool(item.get('is_default', idx == 0))
        sku.is_active = item.get('is_active', True) is not False
        sku.save()
        kept_ids.add(sku.id)
        if first_active is None and sku.is_active:
            first_active = sku
        if sku.is_default:
            default_sku = sku
    product.skus.filter(id__in=(existing_ids - kept_ids)).delete()
    if not default_sku and first_active:
        first_active.is_default = True
        first_active.save(update_fields=['is_default'])
    product.skus.exclude(id=(default_sku or first_active).id if (default_sku or first_active) else None).update(is_default=False)


def sku_schema_ready():
    from django.db import connection
    try:
        tables = connection.introspection.table_names()
        if 'product_sku' not in tables:
            return False
        with connection.cursor() as cursor:
            bead_cols = {c.name for c in connection.introspection.get_table_description(cursor, 'finished_product_bead')}
            acc_cols = {c.name for c in connection.introspection.get_table_description(cursor, 'finished_product_accessory')}
        return 'sku_id' in bead_cols and 'sku_id' in acc_cols
    except Exception:
        return False


def product_skus_payload(product):
    if not sku_schema_ready():
        return []
    return [sku_to_dict(sku) for sku in product.skus.all()]

