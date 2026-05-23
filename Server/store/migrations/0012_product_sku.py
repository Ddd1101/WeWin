# Generated manually for product SKU support
import django.db.models.deletion
from django.db import migrations, models


def seed_default_skus(apps, schema_editor):
    Product = apps.get_model('store', 'Product')
    ProductSku = apps.get_model('store', 'ProductSku')
    Bead = apps.get_model('store', 'Bead')
    Accessory = apps.get_model('store', 'Accessory')
    FinishedProductBead = apps.get_model('store', 'FinishedProductBead')
    FinishedProductAccessory = apps.get_model('store', 'FinishedProductAccessory')

    for product in Product.objects.filter(product_type__in=['bead', 'accessory']):
        if ProductSku.objects.filter(product=product).exists():
            continue
        detail = None
        defaults = {
            'product': product,
            'sku_code': f'{product.code}-默认',
            'name': '默认SKU',
            'purchase_cost': product.purchase_cost,
            'cost_price': product.cost_price,
            'is_default': True,
            'is_active': True,
        }
        if product.product_type == 'bead':
            try:
                detail = Bead.objects.get(product=product)
            except Bead.DoesNotExist:
                detail = None
        elif product.product_type == 'accessory':
            try:
                detail = Accessory.objects.get(product=product)
            except Accessory.DoesNotExist:
                detail = None
        if detail:
            for attr in ['material', 'size', 'color']:
                defaults[attr] = getattr(detail, attr, None)
            if hasattr(detail, 'weight'):
                defaults['weight'] = detail.weight
            if hasattr(detail, 'quality_level'):
                defaults['quality_level'] = detail.quality_level
            if hasattr(detail, 'remark'):
                defaults['remark'] = detail.remark
        ProductSku.objects.create(**defaults)

    for item in FinishedProductBead.objects.filter(sku__isnull=True):
        sku = ProductSku.objects.filter(product=item.bead.product, is_default=True).first() or ProductSku.objects.filter(product=item.bead.product).first()
        if sku:
            item.sku = sku
            item.save(update_fields=['sku'])
    for item in FinishedProductAccessory.objects.filter(sku__isnull=True):
        sku = ProductSku.objects.filter(product=item.accessory.product, is_default=True).first() or ProductSku.objects.filter(product=item.accessory.product).first()
        if sku:
            item.sku = sku
            item.save(update_fields=['sku'])


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0011_alter_accessory_size'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductSku',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku_code', models.CharField(blank=True, default='', max_length=100, verbose_name='SKU编码')),
                ('name', models.CharField(blank=True, default='', max_length=200, verbose_name='SKU名称')),
                ('material', models.CharField(blank=True, max_length=100, null=True, verbose_name='材质')),
                ('size', models.IntegerField(blank=True, null=True, verbose_name='规格')),
                ('color', models.CharField(blank=True, max_length=100, null=True, verbose_name='颜色')),
                ('purchase_cost', models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name='采购成本(元/克)')),
                ('cost_price', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='成本价格')),
                ('weight', models.DecimalField(decimal_places=3, default=0, max_digits=10, verbose_name='克重')),
                ('quality_level', models.IntegerField(default=5, verbose_name='品质等级(1-10)')),
                ('remark', models.TextField(blank=True, null=True, verbose_name='备注')),
                ('is_default', models.BooleanField(default=False, verbose_name='默认SKU')),
                ('is_active', models.BooleanField(default=True, verbose_name='是否启用')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='skus', to='store.product', verbose_name='关联商品')),
            ],
            options={
                'verbose_name': '商品SKU',
                'verbose_name_plural': '商品SKU',
                'db_table': 'product_sku',
                'ordering': ['product_id', '-is_default', 'id'],
            },
        ),
        migrations.AddField(
            model_name='finishedproductbead',
            name='sku',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='finished_bead_items', to='store.productsku', verbose_name='串珠SKU'),
        ),
        migrations.AddField(
            model_name='finishedproductaccessory',
            name='sku',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='finished_accessory_items', to='store.productsku', verbose_name='配件SKU'),
        ),
        migrations.AlterUniqueTogether(
            name='finishedproductbead',
            unique_together={('finished_product', 'bead', 'sku')},
        ),
        migrations.AlterUniqueTogether(
            name='finishedproductaccessory',
            unique_together={('finished_product', 'accessory', 'sku')},
        ),
        migrations.RunPython(seed_default_skus, migrations.RunPython.noop),
    ]
