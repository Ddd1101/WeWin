from decimal import Decimal
from store.models import ProductSku, ProductType


def _finished_cost_breakdown(finished):
    """返回 (串珠成本小计, 配件成本小计)，优先使用 SKU 成本"""
    bead_cost = Decimal('0')
    accessory_cost = Decimal('0')
    for fpb in finished.beads.all():
        if fpb.sku_id and fpb.sku:
            bead_cost += fpb.sku.cost_price * fpb.quantity
        else:
            bead_cost += fpb.bead.product.cost_price * fpb.quantity
    for fpa in finished.accessories.all():
        if fpa.sku_id and fpa.sku:
            accessory_cost += fpa.sku.cost_price * fpa.quantity
        else:
            accessory_cost += fpa.accessory.product.cost_price * fpa.quantity
    return bead_cost, accessory_cost


def _finished_bom_snapshot(finished):
    """构建成品 BOM 快照（串珠/配件明细），用于成本历史可追溯"""
    beads = []
    for fpb in finished.beads.select_related('bead__product', 'sku'):
        unit_cost = fpb.sku.cost_price if (fpb.sku_id and fpb.sku) else fpb.bead.product.cost_price
        beads.append({
            'code': fpb.bead.product.code,
            'sku_code': fpb.sku.sku_code if fpb.sku else None,
            'quantity': fpb.quantity,
            'unit_cost': float(unit_cost),
            'subtotal': float(unit_cost * fpb.quantity),
        })
    accessories = []
    for fpa in finished.accessories.select_related('accessory__product', 'sku'):
        unit_cost = fpa.sku.cost_price if (fpa.sku_id and fpa.sku) else fpa.accessory.product.cost_price
        accessories.append({
            'code': fpa.accessory.product.code,
            'sku_code': fpa.sku.sku_code if fpa.sku else None,
            'quantity': fpa.quantity,
            'unit_cost': float(unit_cost),
            'subtotal': float(unit_cost * fpa.quantity),
        })
    return {'beads': beads, 'accessories': accessories}


def record_finished_cost_history(finished, trigger_reason='', created_by=None):
    """记录成品成本快照（仅当成本或组成发生变化时），返回总成本"""
    from store.models import FinishedProductCostHistory
    bead_cost, accessory_cost = _finished_cost_breakdown(finished)
    total = bead_cost + accessory_cost + finished.labor_cost + finished.elastic_cost
    bom_snapshot = _finished_bom_snapshot(finished)
    last = finished.cost_history.order_by('-created_at').first()
    if last and last.cost_price == total and last.bead_cost == bead_cost and last.accessory_cost == accessory_cost and last.labor_cost == finished.labor_cost and last.elastic_cost == finished.elastic_cost and last.bom_snapshot == bom_snapshot:
        return total

    FinishedProductCostHistory.objects.create(
        finished_product=finished,
        cost_price=total,
        bead_cost=bead_cost,
        accessory_cost=accessory_cost,
        labor_cost=finished.labor_cost,
        elastic_cost=finished.elastic_cost,
        trigger_reason=(trigger_reason.strip() or '成本变动')[:500],
        created_by=created_by,
        bom_snapshot=bom_snapshot,
    )
    return total


def material_cost_change_reason(kind, material_product, old_cost, old_sku_costs=None):
    """生成物料成本变动触发文案：品名 + 货号 + 涨跌金额，优先展示 SKU 明细"""
    label = f'{kind}「{material_product.name or "-"}」(货号 {material_product.code or "-"})'
    skus = list(material_product.skus.all()) if sku_schema_ready() else []
    changes = []
    for sku in skus:
        old = (old_sku_costs or {}).get(sku.id)
        if old is not None and old[1] != sku.cost_price:
            changes.append((sku.sku_code, old[1], sku.cost_price))

    if changes:
        parts = []
        for sku_code, old_value, new_value in changes:
            delta = new_value - old_value
            arrow = '↑' if delta > 0 else '↓' if delta < 0 else '→'
            parts.append(f'{sku_code}{old_value:.2f}→{new_value:.2f}{arrow}')
        return f'{label} 成本变动（{"；".join(parts)}）'

    new_cost = material_product.cost_price
    delta = new_cost - old_cost
    if delta > 0:
        return f'{label} 成本上涨 ¥{delta:.2f}（{old_cost:.2f} → {new_cost:.2f}）'
    if delta < 0:
        return f'{label} 成本下降 ¥{abs(delta):.2f}（{old_cost:.2f} → {new_cost:.2f}）'
    return f'{label} 成本变更'


def recalculate_related_finished_products(material_product, trigger_reason='', created_by=None):
    """物料（串珠/配件）成本变动后，重算所有使用该物料的手串成品成本并记录快照"""
    from store.models import Bead, Accessory, FinishedProduct
    finished_ids = set()
    if material_product.product_type == ProductType.BEAD:
        bead = Bead.objects.filter(product=material_product).first()
        if bead:
            finished_ids = set(bead.finished_products.values_list('finished_product_id', flat=True))
    elif material_product.product_type == ProductType.ACCESSORY:
        accessory = Accessory.objects.filter(product=material_product).first()
        if accessory:
            finished_ids = set(accessory.finished_products.values_list('finished_product_id', flat=True))

    if not finished_ids:
        return

    for finished in FinishedProduct.objects.filter(product_id__in=finished_ids).select_related('product'):
        total = record_finished_cost_history(finished, trigger_reason, created_by)
        finished.product.cost_price = total
        finished.product.save(update_fields=['cost_price'])


def finished_cost_summary(finished):
    """返回成品的历史最高/当前/最低成本"""
    costs = list(finished.cost_history.order_by('created_at').values_list('cost_price', flat=True))
    if not costs:
        return {'highest_cost': None, 'current_cost': None, 'lowest_cost': None}
    return {
        'highest_cost': float(max(costs)),
        'current_cost': float(costs[-1]),
        'lowest_cost': float(min(costs)),
    }


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


_sku_schema_ready_cache = None


def sku_schema_ready():
    global _sku_schema_ready_cache
    if _sku_schema_ready_cache is not None:
        return _sku_schema_ready_cache
    from django.db import connection
    try:
        tables = connection.introspection.table_names()
        if 'product_sku' not in tables:
            _sku_schema_ready_cache = False
            return False
        with connection.cursor() as cursor:
            bead_cols = {c.name for c in connection.introspection.get_table_description(cursor, 'finished_product_bead')}
            acc_cols = {c.name for c in connection.introspection.get_table_description(cursor, 'finished_product_accessory')}
        _sku_schema_ready_cache = 'sku_id' in bead_cols and 'sku_id' in acc_cols
    except Exception:
        _sku_schema_ready_cache = False
    return _sku_schema_ready_cache


def product_skus_payload(product):
    if not sku_schema_ready():
        return []
    return [sku_to_dict(sku) for sku in product.skus.all()]

