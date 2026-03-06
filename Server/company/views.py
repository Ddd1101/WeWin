from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
import json
import jwt
from django.conf import settings

from account.models import User, UserType
from .models import Company


SECRET_KEY = settings.SECRET_KEY


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
        
        if current_user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '无权限更新企业'}, status=403)

        company = Company.objects.get(id=company_id)
        data = json.loads(request.body)

        if 'name' in data:
            if data['name'] != company.name and Company.objects.filter(name=data['name']).exists():
                return JsonResponse({'error': '企业名称已存在'}, status=400)
            company.name = data['name']

        if 'address' in data:
            company.address = data['address']

        if 'contact_name' in data:
            company.contact_name = data['contact_name']

        if 'contact_phone' in data:
            company.contact_phone = data['contact_phone']

        if 'is_active' in data:
            company.is_active = data['is_active']

        company.save()

        if not company.is_active:
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
        
        if current_user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '无权限删除企业'}, status=403)

        company = Company.objects.get(id=company_id)
        
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
        
        if current_user.user_type not in [UserType.SUPER_ADMIN, UserType.SITE_ADMIN]:
            return JsonResponse({'error': '无权限批量更新企业状态'}, status=403)

        data = json.loads(request.body)
        company_ids = data.get('company_ids', [])
        is_active = data.get('is_active')

        if not company_ids or is_active is None:
            return JsonResponse({'error': '企业ID和状态不能为空'}, status=400)

        companies = Company.objects.filter(id__in=company_ids)
        companies.update(is_active=is_active)

        if not is_active:
            for company in companies:
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
