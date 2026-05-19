# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0005_remove_product_temp_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="products/%Y/%m/%d/",
                verbose_name="商品图片",
            ),
        ),
    ]
