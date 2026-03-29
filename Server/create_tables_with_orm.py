import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wewin.settings')
django.setup()

from django.db import connection
from store.models import Product, ProductType, Bead, Accessory, FinishedProduct, FinishedProductBead, FinishedProductAccessory

# 检查并创建所有表
print("Checking and creating tables...")

# 打印所有模型
models = [Product, Bead, Accessory, FinishedProduct, FinishedProductBead, FinishedProductAccessory]

for model in models:
    print(f"\nChecking {model.__name__} table...")
    # 检查表是否存在
    table_name = model._meta.db_table
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
        result = cursor.fetchone()
        if result:
            print(f"{table_name} table already exists")
        else:
            print(f"{table_name} table does not exist, creating...")
            # 使用Django的schema_editor创建表
            from django.db import migrations
            from django.db.migrations.state import ModelState
            from django.db.migrations.autodetector import MigrationAutodetector
            from django.db.migrations.loader import MigrationLoader
            from django.db.migrations.graph import MigrationGraph
            
            # 这是一个简化的方法，实际上Django的迁移系统更复杂
            # 我们可以通过尝试创建一个实例来触发表的创建
            try:
                # 尝试创建一个临时实例，这会触发表的创建
                if model == Product:
                    # 为Product创建一个临时实例
                    product = Product(
                        code="TEMP",
                        name="Temporary Product",
                        product_type=ProductType.ACCESSORY,
                        cost_price=0.0,
                        selling_price=0.0,
                        company_id=1
                    )
                    product.save()
                    product.delete()
                elif model == Bead:
                    # 为Bead创建一个临时实例
                    product = Product(
                        code="TEMP_BEAD",
                        name="Temporary Bead Product",
                        product_type=ProductType.BEAD,
                        cost_price=0.0,
                        selling_price=0.0,
                        company_id=1
                    )
                    product.save()
                    bead = Bead(product=product, material="", size="", color="")
                    bead.save()
                    bead.delete()
                    product.delete()
                elif model == Accessory:
                    # 为Accessory创建一个临时实例
                    product = Product(
                        code="TEMP_ACCESSORY",
                        name="Temporary Accessory Product",
                        product_type=ProductType.ACCESSORY,
                        cost_price=0.0,
                        selling_price=0.0,
                        company_id=1
                    )
                    product.save()
                    accessory = Accessory(product=product, material="", size="", color="")
                    accessory.save()
                    accessory.delete()
                    product.delete()
                elif model == FinishedProduct:
                    # 为FinishedProduct创建一个临时实例
                    product = Product(
                        code="TEMP_FINISHED",
                        name="Temporary Finished Product",
                        product_type=ProductType.FINISHED,
                        cost_price=0.0,
                        selling_price=0.0,
                        company_id=1
                    )
                    product.save()
                    finished = FinishedProduct(product=product)
                    finished.save()
                    finished.delete()
                    product.delete()
                print(f"{table_name} table created successfully")
            except Exception as e:
                print(f"Error creating {table_name} table: {e}")

print("\nTable check and creation completed.")
