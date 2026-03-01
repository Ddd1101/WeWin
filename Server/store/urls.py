from django.urls import path
from . import views

urlpatterns = [
    path('platforms/', views.get_platforms, name='get-platforms'),
    path('categories/', views.get_categories, name='get-categories'),
    path('', views.get_stores, name='get-stores'),
    path('create/', views.create_store, name='create-store'),
    path('<int:store_id>/update/', views.update_store, name='update-store'),
    path('<int:store_id>/delete/', views.delete_store, name='delete-store'),
    path('<int:store_id>/api-config/', views.get_store_api_config, name='get-store-api-config'),
    path('<int:store_id>/api-config/create-or-update/', views.create_or_update_api_config, name='create-or-update-api-config'),
    path('<int:store_id>/trigger-pull/', views.trigger_data_pull, name='trigger-data-pull'),
    path('<int:store_id>/orders/', views.get_orders, name='get-orders'),
    path('<int:store_id>/pull-tasks/', views.get_pull_tasks, name='get-pull-tasks'),
]
