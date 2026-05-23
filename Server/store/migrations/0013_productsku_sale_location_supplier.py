# Generated manually for SKU-owned sales and storage fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('store', '0012_product_sku'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsku',
            name='selling_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='售卖价格'),
        ),
        migrations.AddField(
            model_name='productsku',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='库位'),
        ),
        migrations.AddField(
            model_name='productsku',
            name='supplier',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='供应商'),
        ),
    ]
