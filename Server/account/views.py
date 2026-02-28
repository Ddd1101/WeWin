from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from .models import User, Company, UserType, PageConfig
import json
from datetime import datetime, timedelta
import jwt
from django.conf import settings
import random
import string


def generate_company_code():
    last_company = Company.objects.order_by('-id').first()
    if last_company:
        try:
            last_code = int(last_company.code)
            new_code = last_code + 1
        except ValueError:
            new_code = 10000001
    else:
        new_code = 10000001
    
    code_str = str(new_code).zfill(8)
    while Company.objects.filter(code=code_str).exists():
        new_code += 1
        code_str = str(new_code).zfill(8)
    
    return code_str


SECRET_KEY = settings.SECRET_KEY


def generate_token(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'user_type': user.user_type,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')


@csrf_exempt
@require_http_methods(['POST'])
def login_view(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({'error': '用户名和密码不能为空'}, status=400)

        # 先通过用户名获取用户对象，不检查激活状态
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({'error': '用户名或密码错误'}, status=401)
        
        # 检查密码
        if not user.check_password(password):
            return JsonResponse({'error': '用户名或密码错误'}, status=401)
        
        # 检查账户是否激活
        if not user.is_active:
            return JsonResponse({'error': '账户已被禁用'}, status=403)

        token = generate_token(user)

        return JsonResponse({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'email': user.email,
                'phone': user.phone,
                'real_name': user.real_name,
                'company_id': user.company_id if user.company else None,
                'company_name': user.company.name if user.company else None
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def logout_view(request):
    logout(request)
    return JsonResponse({'message': '登出成功'})


@csrf_exempt
@require_http_methods(['POST'])
def create_enterprise_admin(request):
    try:
        data = json.loads(request.body)
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        phone = data.get('phone', '')
        real_name = data.get('real_name', '')
        
        company_name = data.get('company_name')
        company_code = data.get('company_code')
        company_address = data.get('company_address', '')
        company_contact_name = data.get('company_contact_name', '')
        company_contact_phone = data.get('company_contact_phone', '')

        if not all([username, password, company_name, company_code]):
            return JsonResponse({'error': '必填字段不能为空'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': '用户名已存在'}, status=400)

        if Company.objects.filter(name=company_name).exists():
            return JsonResponse({'error': '企业名称已存在'}, status=400)

        if Company.objects.filter(code=company_code).exists():
            return JsonResponse({'error': '企业编号已存在'}, status=400)

        with transaction.atomic():
            company = Company.objects.create(
                name=company_name,
                code=company_code,
                address=company_address,
                contact_name=company_contact_name,
                contact_phone=company_contact_phone
            )

            user = User.objects.create_user(
                username=username,
                password=password,
                email=email,
                user_type=UserType.ENTERPRISE_LEADER,
                company=company,
                phone=phone,
                real_name=real_name
            )

        token = generate_token(user)

        return JsonResponse({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'email': user.email,
                'phone': user.phone,
                'real_name': user.real_name,
                'company_id': company.id,
                'company_name': company.name
            }
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_enterprise_user(request):
    try:
        data = json.loads(request.body)
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        phone = data.get('phone', '')
        real_name = data.get('real_name', '')
        company_identifier = data.get('company_identifier')

        if not all([username, password, company_identifier]):
            return JsonResponse({'error': '必填字段不能为空'}, status=400)

        company = Company.objects.filter(name=company_identifier).first()
        if not company:
            company = Company.objects.filter(code=company_identifier).first()

        if not company:
            return JsonResponse({'error': '企业不存在'}, status=404)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': '用户名已存在'}, status=400)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            user_type=UserType.ENTERPRISE_USER,
            company=company,
            phone=phone,
            real_name=real_name
        )

        token = generate_token(user)

        return JsonResponse({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'email': user.email,
                'phone': user.phone,
                'real_name': user.real_name,
                'company_id': company.id,
                'company_name': company.name
            }
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_users(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        users = []
        if current_user.user_type == UserType.SUPER_ADMIN:
            users = User.objects.all()
        elif current_user.user_type == UserType.SITE_ADMIN:
            users = User.objects.exclude(user_type=UserType.SUPER_ADMIN)
        elif current_user.user_type == UserType.ENTERPRISE_LEADER:
            users = User.objects.filter(company=current_user.company)
        elif current_user.user_type == UserType.ENTERPRISE_ADMIN:
            users = User.objects.filter(company=current_user.company)
        else:
            return JsonResponse({'error': '无权限查看用户'}, status=403)

        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'user_type_display': user.get_user_type_display(),
                'email': user.email,
                'phone': user.phone,
                'real_name': user.real_name,
                'company_id': user.company_id,
                'company_name': user.company.name if user.company else None,
                'company_code': user.company.code if user.company else None,
                'company_is_active': user.company.is_active if user.company else None,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat()
            })

        return JsonResponse({'users': user_list})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_companies(request):
    try:
        companies = Company.objects.all()
        company_list = []
        for company in companies:
            company_list.append({
                'id': company.id,
                'name': company.name,
                'code': company.code
            })
        return JsonResponse({'companies': company_list})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_user(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        phone = data.get('phone', '')
        real_name = data.get('real_name', '')
        user_type = data.get('user_type')
        company_id = data.get('company_id')

        if not all([username, password, user_type]):
            return JsonResponse({'error': '必填字段不能为空'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': '用户名已存在'}, status=400)

        company = None
        if company_id:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return JsonResponse({'error': '企业不存在'}, status=404)

        has_permission = False
        if current_user.user_type == UserType.SUPER_ADMIN:
            has_permission = True
        elif current_user.user_type == UserType.SITE_ADMIN:
            if user_type != UserType.SUPER_ADMIN:
                has_permission = True
        elif current_user.user_type == UserType.ENTERPRISE_LEADER:
            if user_type in [UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER] and company == current_user.company:
                has_permission = True
        elif current_user.user_type == UserType.ENTERPRISE_ADMIN:
            if user_type == UserType.ENTERPRISE_USER and company == current_user.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限创建该类型用户'}, status=403)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            user_type=user_type,
            company=company,
            phone=phone,
            real_name=real_name,
            created_by=current_user
        )

        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'user_type_display': user.get_user_type_display(),
            'email': user.email,
            'phone': user.phone,
            'real_name': user.real_name,
            'company_id': user.company_id,
            'company_name': user.company.name if user.company else None,
            'company_code': user.company.code if user.company else None,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat()
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_page_config(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        user_type = payload['user_type']
        configs = PageConfig.objects.filter(user_type=user_type, is_visible=True).order_by('order')
        
        pages = []
        for config in configs:
            pages.append({
                'name': config.page_name,
                'route': config.page_route,
                'order': config.order
            })

        return JsonResponse({'pages': pages})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['PUT'])
def update_user_status(request, user_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        target_user = User.objects.get(id=user_id)
        
        has_permission = False
        if current_user.user_type == UserType.SUPER_ADMIN:
            if target_user.user_type != UserType.SUPER_ADMIN:
                has_permission = True
        elif current_user.user_type == UserType.SITE_ADMIN:
            if target_user.user_type != UserType.SUPER_ADMIN:
                has_permission = True
        elif current_user.user_type == UserType.ENTERPRISE_LEADER:
            if target_user.user_type in [UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER] and target_user.company == current_user.company:
                has_permission = True
        elif current_user.user_type == UserType.ENTERPRISE_ADMIN:
            if target_user.user_type == UserType.ENTERPRISE_USER and target_user.company == current_user.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限修改该用户'}, status=403)

        data = json.loads(request.body)
        is_active = data.get('is_active')
        
        if is_active is not None:
            # 检查用户所属的企业是否被禁用
            if is_active and target_user.company and not target_user.company.is_active:
                return JsonResponse({'error': '企业已被禁用，无法激活该用户'}, status=400)
            
            target_user.is_active = is_active
            target_user.save()

        return JsonResponse({
            'id': target_user.id,
            'username': target_user.username,
            'is_active': target_user.is_active
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['DELETE'])
def delete_user(request, user_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        target_user = User.objects.get(id=user_id)
        
        has_permission = False
        if current_user.user_type == UserType.SUPER_ADMIN:
            has_permission = True
        elif current_user.user_type == UserType.SITE_ADMIN:
            if target_user.user_type != UserType.SUPER_ADMIN:
                has_permission = True
        elif current_user.user_type == UserType.ENTERPRISE_LEADER:
            if target_user.user_type in [UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER] and target_user.company == current_user.company:
                has_permission = True
        elif current_user.user_type == UserType.ENTERPRISE_ADMIN:
            if target_user.user_type == UserType.ENTERPRISE_USER and target_user.company == current_user.company:
                has_permission = True

        if not has_permission:
            return JsonResponse({'error': '无权限删除该用户'}, status=403)

        if target_user.id == current_user.id:
            return JsonResponse({'error': '不能删除自己'}, status=400)

        target_user.delete()
        return JsonResponse({'message': '删除成功'})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['PUT'])
def update_user_type(request, user_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        target_user = User.objects.get(id=user_id)
        
        # 只有网站超级管理员可以变更用户类型
        if current_user.user_type != UserType.SUPER_ADMIN:
            return JsonResponse({'error': '无权限变更用户类型'}, status=403)

        # 只能变更临时账户或网站管理员的类型
        if target_user.user_type not in [UserType.TEMPORARY, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '只能变更临时账户或网站管理员的类型'}, status=400)

        data = json.loads(request.body)
        user_type = data.get('user_type')
        
        if not user_type:
            return JsonResponse({'error': '用户类型不能为空'}, status=400)

        # 验证用户类型是否有效
        valid_user_types = [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]
        if user_type not in valid_user_types:
            return JsonResponse({'error': '无效的用户类型'}, status=400)

        # 更新用户类型
        target_user.user_type = user_type
        target_user.save()

        return JsonResponse({
            'id': target_user.id,
            'username': target_user.username,
            'user_type': target_user.user_type,
            'user_type_display': target_user.get_user_type_display()
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def simple_register(request):
    try:
        data = json.loads(request.body)
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')
        phone = data.get('phone', '')
        real_name = data.get('real_name', '')
        
        if not all([username, password]):
            return JsonResponse({'error': '用户名和密码不能为空'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': '用户名已存在'}, status=400)
        
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            phone=phone,
            real_name=real_name,
            user_type=UserType.TEMPORARY
        )
        
        token = generate_token(user)
        
        return JsonResponse({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'user_type': user.user_type,
                'user_type_display': user.get_user_type_display(),
                'email': user.email,
                'phone': user.phone,
                'real_name': user.real_name,
                'company_id': None,
                'company_name': None
            }
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_current_user(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)
        
        user = User.objects.get(id=payload['user_id'])
        
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'user_type_display': user.get_user_type_display(),
            'email': user.email,
            'phone': user.phone,
            'real_name': user.real_name,
            'company_id': user.company_id,
            'company_name': user.company.name if user.company else None,
            'company_code': user.company.code if user.company else None
        })
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_and_bind_company(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)
        
        user = User.objects.get(id=payload['user_id'])
        
        if user.company:
            return JsonResponse({'error': '您已经绑定了企业'}, status=400)
        
        data = json.loads(request.body)
        company_name = data.get('company_name')
        company_address = data.get('company_address', '')
        company_contact_name = data.get('company_contact_name', '')
        company_contact_phone = data.get('company_contact_phone', '')
        
        if not company_name:
            return JsonResponse({'error': '企业名称不能为空'}, status=400)
        
        if Company.objects.filter(name=company_name).exists():
            return JsonResponse({'error': '企业名称已存在'}, status=400)
        
        with transaction.atomic():
            company_code = generate_company_code()
            company = Company.objects.create(
                name=company_name,
                code=company_code,
                address=company_address,
                contact_name=company_contact_name,
                contact_phone=company_contact_phone
            )
            
            user.company = company
            user.user_type = UserType.ENTERPRISE_LEADER
            user.save()
        
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'user_type_display': user.get_user_type_display(),
            'email': user.email,
            'phone': user.phone,
            'company_id': company.id,
            'company_name': company.name,
            'company_code': company.code
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def bind_existing_company(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)
        
        user = User.objects.get(id=payload['user_id'])
        
        if user.company:
            return JsonResponse({'error': '您已经绑定了企业'}, status=400)
        
        data = json.loads(request.body)
        company_code = data.get('company_code')
        
        if not company_code:
            return JsonResponse({'error': '企业编号不能为空'}, status=400)
        
        company = Company.objects.filter(code=company_code).first()
        if not company:
            return JsonResponse({'error': '企业不存在'}, status=404)
        
        user.company = company
        user.user_type = UserType.ENTERPRISE_USER
        user.save()
        
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'user_type_display': user.get_user_type_display(),
            'email': user.email,
            'phone': user.phone,
            'company_id': company.id,
            'company_name': company.name,
            'company_code': company.code
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['PUT'])
def update_profile(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)
        
        user = User.objects.get(id=payload['user_id'])
        
        data = json.loads(request.body)
        email = data.get('email')
        phone = data.get('phone')
        real_name = data.get('real_name')
        
        if email:
            user.email = email
        if phone:
            user.phone = phone
        if real_name:
            user.real_name = real_name
        
        user.save()
        
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'user_type_display': user.get_user_type_display(),
            'email': user.email,
            'phone': user.phone,
            'real_name': user.real_name,
            'company_id': user.company_id,
            'company_name': user.company.name if user.company else None,
            'company_code': user.company.code if user.company else None
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def change_password(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)
        
        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)
        
        user = User.objects.get(id=payload['user_id'])
        
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return JsonResponse({'error': '旧密码和新密码不能为空'}, status=400)
        
        if not user.check_password(old_password):
            return JsonResponse({'error': '旧密码错误'}, status=400)
        
        user.set_password(new_password)
        user.save()
        
        return JsonResponse({'message': '密码修改成功'})
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# 企业管理相关视图函数
@require_http_methods(['GET'])
def get_companies(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        # 只有超级管理员和网站管理员可以查看所有企业
        if current_user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '无权限查看企业列表'}, status=403)

        companies = Company.objects.all()
        company_list = []
        for company in companies:
            company_list.append({
                'id': company.id,
                'name': company.name,
                'code': company.code,
                'address': company.address,
                'contact_name': company.contact_name,
                'contact_phone': company.contact_phone,
                'is_active': company.is_active,
                'created_at': company.created_at.isoformat()
            })
        return JsonResponse({'companies': company_list})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def create_company(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        # 只有超级管理员和网站管理员可以创建企业
        if current_user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '无权限创建企业'}, status=403)

        data = json.loads(request.body)
        name = data.get('name')
        address = data.get('address', '')
        contact_name = data.get('contact_name', '')
        contact_phone = data.get('contact_phone', '')

        if not name:
            return JsonResponse({'error': '企业名称不能为空'}, status=400)

        if Company.objects.filter(name=name).exists():
            return JsonResponse({'error': '企业名称已存在'}, status=400)

        # 自动生成企业编号
        code = generate_company_code()

        company = Company.objects.create(
            name=name,
            code=code,
            address=address,
            contact_name=contact_name,
            contact_phone=contact_phone
        )

        return JsonResponse({
            'id': company.id,
            'name': company.name,
            'code': company.code,
            'address': company.address,
            'contact_name': company.contact_name,
            'contact_phone': company.contact_phone,
            'is_active': company.is_active,
            'created_at': company.created_at.isoformat()
        }, status=201)
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['PUT'])
def update_company(request, company_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        # 只有超级管理员和网站管理员可以更新企业
        if current_user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '无权限更新企业'}, status=403)

        company = Company.objects.get(id=company_id)
        data = json.loads(request.body)

        if 'name' in data:
            if data['name'] != company.name and Company.objects.filter(name=data['name']).exists():
                return JsonResponse({'error': '企业名称已存在'}, status=400)
            company.name = data['name']

        # 企业编号不允许修改

        if 'address' in data:
            company.address = data['address']

        if 'contact_name' in data:
            company.contact_name = data['contact_name']

        if 'contact_phone' in data:
            company.contact_phone = data['contact_phone']

        if 'is_active' in data:
            company.is_active = data['is_active']

        company.save()

        # 当企业被禁用时，禁用其下的非管理员用户
        if not company.is_active:
            # 禁用企业下的非管理员用户（企业负责人、企业用户管理员和企业用户普通账户）
            User.objects.filter(
                company=company,
                user_type__in=[UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]
            ).update(is_active=False)

        return JsonResponse({
            'id': company.id,
            'name': company.name,
            'code': company.code,
            'address': company.address,
            'contact_name': company.contact_name,
            'contact_phone': company.contact_phone,
            'is_active': company.is_active,
            'created_at': company.created_at.isoformat()
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'error': '企业不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['DELETE'])
def delete_company(request, company_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        # 只有超级管理员和网站管理员可以删除企业
        if current_user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '无权限删除企业'}, status=403)

        company = Company.objects.get(id=company_id)
        
        # 检查企业下是否有用户
        if company.users.exists():
            return JsonResponse({'error': '企业下存在用户，无法删除'}, status=400)

        company.delete()
        return JsonResponse({'message': '企业删除成功'})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'error': '企业不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(['GET'])
def get_company_users(request, company_id):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        # 只有超级管理员和网站管理员可以查看企业用户
        if current_user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '无权限查看企业用户'}, status=403)

        company = Company.objects.get(id=company_id)
        users = User.objects.filter(company=company)

        user_list = []
        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'real_name': user.real_name,
                'user_type': user.user_type,
                'user_type_display': user.get_user_type_display(),
                'email': user.email,
                'phone': user.phone,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat()
            })

        return JsonResponse({'users': user_list})
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'error': '企业不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def batch_update_company_status(request):
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '未授权'}, status=401)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return JsonResponse({'error': 'Token已过期'}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({'error': '无效的Token'}, status=401)

        current_user = User.objects.get(id=payload['user_id'])
        
        # 只有超级管理员和网站管理员可以批量更新企业状态
        if current_user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '无权限批量更新企业状态'}, status=403)

        data = json.loads(request.body)
        company_ids = data.get('company_ids', [])
        is_active = data.get('is_active')

        if not company_ids or is_active is None:
            return JsonResponse({'error': '企业ID和状态不能为空'}, status=400)

        # 批量更新企业状态
        companies = Company.objects.filter(id__in=company_ids)
        companies.update(is_active=is_active)

        # 当企业被禁用时，禁用其下的非管理员用户
        if not is_active:
            for company in companies:
                # 禁用企业下的非管理员用户（企业负责人、企业用户管理员和企业用户普通账户）
                User.objects.filter(
                    company=company,
                    user_type__in=[UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN, UserType.ENTERPRISE_USER]
                ).update(is_active=False)

        return JsonResponse({'message': '批量更新企业状态成功'})
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'error': '用户不存在'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)