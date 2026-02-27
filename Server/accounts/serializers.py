from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Enterprise, UserType


User = get_user_model()


class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.CharField(source='enterprise.name', read_only=True)
    user_type_display = serializers.CharField(source='get_user_type_display', read_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'user_type_display', 'enterprise', 'enterprise_name',
            'phone', 'avatar', 'is_active', 'is_staff',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    enterprise_name = serializers.CharField(write_only=True, required=False)
    enterprise_code = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'phone', 'user_type',
            'enterprise', 'enterprise_name', 'enterprise_code'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("密码不匹配")
        
        user_type = data.get('user_type')
        
        if user_type == UserType.ENTERPRISE_ADMIN:
            if not data.get('enterprise_name') or not data.get('enterprise_code'):
                raise serializers.ValidationError("企业管理员需要提供企业名称和编号")
        elif user_type == UserType.ENTERPRISE_USER:
            if not data.get('enterprise'):
                raise serializers.ValidationError("企业普通用户需要选择所属企业")
        
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        enterprise_name = validated_data.pop('enterprise_name', None)
        enterprise_code = validated_data.pop('enterprise_code', None)
        
        user_type = validated_data.get('user_type')
        
        if user_type == UserType.ENTERPRISE_ADMIN:
            enterprise, created = Enterprise.objects.get_or_create(
                code=enterprise_code,
                defaults={'name': enterprise_name}
            )
            validated_data['enterprise'] = enterprise
        
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user
