from django.urls import path
from . import views

urlpatterns = [
    # 客户 CRUD
    path('', views.get_customers, name='get-customers'),
    path('create/', views.create_customer, name='create-customer'),
    path('<int:customer_id>/update/', views.update_customer, name='update-customer'),
    path('<int:customer_id>/delete/', views.delete_customer, name='delete-customer'),
    path('<int:customer_id>/detail/', views.get_customer_detail, name='get-customer-detail'),
    
    # 客户商品关联
    path('<int:customer_id>/products/', views.get_customer_products, name='get-customer-products'),
    path('<int:customer_id>/products/create-or-update/', views.create_or_update_customer_product, name='create-or-update-customer-product'),
    path('<int:customer_id>/products/<int:customer_product_id>/delete/', views.delete_customer_product, name='delete-customer-product'),
    path('<int:customer_id>/products/<int:product_id>/price-history/', views.get_customer_price_history, name='get-customer-price-history'),
    
    # 客户可见性配置
    path('<int:customer_id>/visibility/', views.get_customer_visibility, name='get-customer-visibility'),
    path('<int:customer_id>/visibility/set/', views.set_customer_visibility, name='set-customer-visibility'),
    path('<int:customer_id>/visibility/<int:visibility_id>/delete/', views.remove_customer_visibility, name='remove-customer-visibility'),
]
