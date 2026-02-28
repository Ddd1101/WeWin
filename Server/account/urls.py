from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.simple_register, name='simple-register'),
    path('current-user/', views.get_current_user, name='get-current-user'),
    path('profile/update/', views.update_profile, name='update-profile'),
    path('password/change/', views.change_password, name='change-password'),
    path('create-enterprise-admin/', views.create_enterprise_admin, name='create-enterprise-admin'),
    path('create-enterprise-user/', views.create_enterprise_user, name='create-enterprise-user'),
    path('create-and-bind-company/', views.create_and_bind_company, name='create-and-bind-company'),
    path('bind-existing-company/', views.bind_existing_company, name='bind-existing-company'),
    path('users/', views.get_users, name='get-users'),
    path('users/create/', views.create_user, name='create-user'),
    path('users/<int:user_id>/status/', views.update_user_status, name='update-user-status'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete-user'),
    path('users/<int:user_id>/update-type/', views.update_user_type, name='update-user-type'),
    path('companies/', views.get_companies, name='get-companies'),
    path('companies/', views.create_company, name='create-company'),
    path('companies/<int:company_id>/', views.update_company, name='update-company'),
    path('companies/<int:company_id>/', views.delete_company, name='delete-company'),
    path('companies/<int:company_id>/users/', views.get_company_users, name='get-company-users'),
    path('page-config/', views.get_page_config, name='get-page-config'),
]
