"""
共享装饰器模块
用于统一处理认证、权限验证等
"""
import jwt
from functools import wraps
from django.http import JsonResponse
from django.conf import settings
from account.models import User, UserType


def jwt_required(view_func):
    """
    JWT 认证装饰器
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            return JsonResponse({'error': '用户不存在'}, status=404)

        # 将用户信息附加到 request 对象上
        request.user = user
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def permission_required(allowed_user_types):
    """
    权限验证装饰器
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request, 'user'):
                return JsonResponse({'error': '未授权'}, status=401)

            if request.user.user_type not in allowed_user_types:
                return JsonResponse({'error': '无权限操作'}, status=403)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """
    超级管理员或网站管理员权限装饰器
    """
    return permission_required([UserType.SUPER_ADMIN, UserType.SITE_ADMIN])


def enterprise_leader_required(view_func):
    """
    企业负责人权限装饰器（包括管理员）
    """
    return permission_required([
        UserType.SUPER_ADMIN,
        UserType.SITE_ADMIN,
        UserType.ENTERPRISE_LEADER
    ])
