"""Product images: validate content, preserve old files until the DB commits."""
import logging
import os
import uuid
import warnings
import json
import time
import hashlib
from contextvars import ContextVar
from functools import wraps
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage, default_storage
from django.db import transaction
from django.http import JsonResponse

logger = logging.getLogger(__name__)
prepared_image = ContextVar('prepared_product_image', default=None)
created_files = ContextVar('created_product_images', default=None)


class StorageUnavailable(OSError):
    pass


def check_media():
    if getattr(settings, 'MEDIA_ORIGIN_URL', ''):
        from .remote_media import remote_request
        if remote_request('GET', '/health').status_code != 200:
            raise StorageUnavailable('N1 图片服务不可用')
        return
    root = Path(settings.MEDIA_ROOT)
    if settings.MEDIA_REQUIRE_MOUNT and not os.path.ismount(root):
        raise StorageUnavailable('媒体存储未挂载')
    if settings.MEDIA_PROBE_FILE:
        try:
            if (root / settings.MEDIA_PROBE_FILE).read_bytes() != b'wewin-media-ready\n':
                raise StorageUnavailable('媒体探测失败')
        except OSError as exc:
            raise StorageUnavailable('媒体存储不可用') from exc


def validate_image(content):
    if content.size > settings.PRODUCT_IMAGE_MAX_BYTES:
        raise ValidationError('图片不能超过 100MB')
    try:
        content.seek(0)
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(content) as image:
                extension = {'JPEG': '.jpg', 'PNG': '.png', 'WEBP': '.webp', 'GIF': '.gif'}.get(image.format)
                if not extension:
                    raise ValidationError('仅支持 JPEG、PNG、WebP、GIF 图片')
                image.verify()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ValidationError('图片内容无效或分辨率过大') from exc
    finally:
        content.seek(0)
    return extension


class ProductImageStorage(FileSystemStorage):
    def _save(self, name, content):
        check_media()
        suffix = validate_image(content)
        name = str(Path(name).parent / (uuid.uuid4().hex + suffix))
        try:
            saved = super()._save(name, content)
        except OSError as exc:
            logger.exception('Image write failed')
            raise StorageUnavailable('媒体写入失败，请稍后重试') from exc
        pending = created_files.get()
        if pending is not None:
            pending.append(saved)
        return saved

    def delete(self, name):
        check_media()
        return super().delete(name)


def queue_cleanup(name, reason, delay=0):
    directory = Path(settings.MEDIA_CLEANUP_DIR)
    directory.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha256(name.encode()).hexdigest()
    target = directory / (key + '.json')
    if target.exists() and reason == 'orphan':
        return
    temporary = directory / (key + '.' + uuid.uuid4().hex + '.tmp')
    temporary.write_text(json.dumps({'name': name, 'reason': reason, 'due': time.time() + delay}))
    temporary.replace(target)


def image_value(content):
    prepared = prepared_image.get()
    if prepared and content is prepared[0]:
        return prepared[1]
    return content


def delete_image_after_commit(name):
    if name:
        if getattr(settings, 'MEDIA_ORIGIN_URL', ''):
            # Durable before commit; cleanup rechecks references after commit.
            queue_cleanup(name, 'obsolete', delay=60)
        else:
            check_media()
            transaction.on_commit(lambda: cleanup_image(name))


def cleanup_image(name):
    try:
        default_storage.delete(name)
    except Exception:
        logger.exception('Deferred image cleanup required: %s', name)


def product_mutation(view):
    """Also roll back views that catch exceptions and return an error response."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        files = []
        token = created_files.set(files)
        cleanup_confirmed = False
        image_token = None
        try:
            if getattr(settings, 'MEDIA_ORIGIN_URL', ''):
                from account.models import UserType
                from store.models import Product
                data = None
                upload = None
                if request.content_type and 'multipart/form-data' in request.content_type:
                    if request.method == 'PUT':
                        from django.http.multipartparser import MultiPartParser
                        data, files_dict = MultiPartParser(request.META, request, request.upload_handlers, request.encoding).parse()
                    else:
                        data, files_dict = request.POST, request.FILES
                    request._wewin_multipart = (data, files_dict)
                    upload = files_dict.get('image')
                if not upload:
                    removes_image = request.method == 'DELETE'
                    if data is not None:
                        removes_image = removes_image or str(data.get('remove_image', '')).lower() == 'true'
                    elif request.content_type == 'application/json':
                        try:
                            removes_image = removes_image or json.loads(request.body).get('remove_image') is True
                        except (ValueError, TypeError):
                            pass
                    if removes_image and 'product_id' in kwargs:
                        target = Product.objects.filter(pk=kwargs['product_id']).first()
                        if target and target.image:
                            check_media()
                if upload:
                    if request.user.user_type not in (UserType.SUPER_ADMIN, UserType.SITE_ADMIN):
                        if request.user.user_type not in (UserType.ENTERPRISE_LEADER, UserType.ENTERPRISE_ADMIN):
                            return JsonResponse({'error': '无权限修改商品图片'}, status=403)
                        if 'product_id' in kwargs:
                            product = Product.objects.filter(pk=kwargs['product_id']).first()
                            if product is None or product.company_id != request.user.company_id:
                                return JsonResponse({'error': '无权限访问该商品'}, status=403)
                        elif not request.user.company_id or (data.get('company_id') and str(request.user.company_id) != data.get('company_id')):
                            return JsonResponse({'error': '无权限访问该企业'}, status=403)
                    extension = validate_image(upload)
                    field = Product._meta.get_field('image')
                    key = field.generate_filename(Product(), uuid.uuid4().hex + extension)
                    # Complete all remote I/O before acquiring the SQLite write lock.
                    saved = default_storage.save(key, upload)
                    image_token = prepared_image.set((upload, saved))
            with transaction.atomic():
                if 'product_id' in kwargs:
                    from store.models import Product
                    # SQLite uses BEGIN IMMEDIATE; MariaDB uses a row lock.
                    list(Product.objects.select_for_update().filter(pk=kwargs['product_id']))
                response = view(request, *args, **kwargs)
                if response.status_code >= 400:
                    transaction.set_rollback(True)
            cleanup_confirmed = response.status_code >= 400
            return response
        except StorageUnavailable:
            cleanup_confirmed = True
            return JsonResponse({'error': '媒体存储暂不可用，请稍后重试'}, status=503)
        except ValidationError as exc:
            cleanup_confirmed = True
            return JsonResponse({'error': '; '.join(exc.messages)}, status=400)
        except OSError:
            if getattr(settings, 'MEDIA_ORIGIN_URL', ''):
                cleanup_confirmed = True
                return JsonResponse({'error': '图片暂存或存储不可用，请稍后重试'}, status=503)
            raise
        finally:
            created_files.reset(token)
            if image_token is not None:
                prepared_image.reset(image_token)
            if cleanup_confirmed:
                for name in files:
                    cleanup_image(name)
    return wrapped
