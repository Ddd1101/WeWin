from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import get_user_model, login, logout
from .models import Enterprise, UserType
from .serializers import (
    UserSerializer,
    EnterpriseSerializer,
    UserRegistrationSerializer
)

User = get_user_model()


class EnterpriseViewSet(viewsets.ModelViewSet):
    queryset = Enterprise.objects.all()
    serializer_class = EnterpriseSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'register':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action in ['register', 'login', 'logout']:
            return [AllowAny()]
        if self.action in ['me', 'update_me']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        user = self.request.user
        if user.is_super_admin or user.is_site_admin:
            return User.objects.all()
        elif user.is_enterprise_admin:
            return User.objects.filter(enterprise=user.enterprise)
        return User.objects.filter(id=user.id)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return Response(UserSerializer(user).data)
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=['post'])
    def logout(self, request):
        logout(request)
        return Response({'success': 'Logged out'})

    @action(detail=False, methods=['get'])
    def me(self, request):
        return Response(UserSerializer(request.user).data)

    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_enterprise_admin:
            serializer.save(enterprise=user.enterprise)
        else:
            serializer.save()

    def perform_update(self, serializer):
        user = self.request.user
        instance = self.get_object()
        if user.is_enterprise_admin and instance.enterprise != user.enterprise:
            raise PermissionDenied("You can only manage users in your enterprise")
        serializer.save()
