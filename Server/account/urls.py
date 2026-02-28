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
    path('companies/', views.get_companies, name='get-companies'),
    path('page-config/', views.get_page_config, name='get-page-config'),
]
