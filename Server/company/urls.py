from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_companies, name='get-companies'),
    path('create/', views.create_company, name='create-company'),
    path('<int:company_id>/update/', views.update_company, name='update-company'),
    path('<int:company_id>/delete/', views.delete_company, name='delete-company'),
    path('<int:company_id>/users/', views.get_company_users, name='get-company-users'),
    path('batch-status/', views.batch_update_company_status, name='batch-update-company-status'),
]
