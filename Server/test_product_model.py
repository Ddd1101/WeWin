import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wewin.settings')
django.setup()

from store.models import Product, ProductType
from company.models import Company
from account.models import User

print("Testing Product model...")

# 尝试获取所有产品
print("\nTrying to get all products...")
try:
    products = Product.objects.all()
    print(f"Found {products.count()} products")
except Exception as e:
    print(f"Error getting products: {e}")

# 尝试创建一个产品
print("\nTrying to create a product...")
try:
    # 获取默认公司
    company = Company.objects.first()
    if not company:
        print("No company found, creating one...")
        company = Company.objects.create(name="Test Company", code="TEST")
    
    # 获取默认用户
    user = User.objects.first()
    if not user:
        print("No user found, creating one...")
        user = User.objects.create(username="testuser", password="testpass")
    
    # 创建产品
    product = Product.objects.create(
        code="TEST001",
        name="Test Product",
        product_type=ProductType.ACCESSORY,
        cost_price=10.0,
        selling_price=20.0,
        company=company,
        created_by=user
    )
    print(f"Product created successfully: {product}")
except Exception as e:
    print(f"Error creating product: {e}")

print("\nTest completed.")
