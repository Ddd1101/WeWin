from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, EnterpriseViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'enterprises', EnterpriseViewSet, basename='enterprise')

urlpatterns = [
    path('', include(router.urls)),
]
