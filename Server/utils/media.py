"""Product images: validate content, preserve old files until the DB commits."""
import logging
import os
import uuid
import warnings
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
created_files = ContextVar('created_product_images', default=None)


class StorageUnavailable(OSError):
    pass


def check_media():
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


def delete_image_after_commit(name):
    if name:
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
        try:
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
        finally:
            created_files.reset(token)
            if cleanup_confirmed:
                for name in files:
                    cleanup_image(name)
    return wrapped
