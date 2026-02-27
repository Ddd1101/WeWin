from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('create-enterprise-admin/', views.create_enterprise_admin, name='create-enterprise-admin'),
    path('create-enterprise-user/', views.create_enterprise_user, name='create-enterprise-user'),
    path('users/', views.get_users, name='get-users'),
    path('page-config/', views.get_page_config, name='get-page-config'),
]
