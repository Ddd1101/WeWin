from django.urls import path
from . import views

urlpatterns = [
    path('platforms/', views.get_platforms, name='get-platforms'),
    path('categories/', views.get_categories, name='get-categories'),
    path('', views.get_stores, name='get-stores'),
    path('create/', views.create_store, name='create-store'),
    path('<int:store_id>/update/', views.update_store, name='update-store'),
    path('<int:store_id>/delete/', views.delete_store, name='delete-store'),
]
