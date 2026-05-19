# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0009_product_purchase_cost_alter_product_cost_price"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bead",
            name="size",
            field=models.DecimalField(
                blank=True,
                decimal_places=1,
                max_digits=10,
                null=True,
                verbose_name="尺寸",
            ),
        ),
    ]
