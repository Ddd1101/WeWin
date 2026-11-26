import json
import logging
import time
from pathlib import Path
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from utils.media import check_media

logger = logging.getLogger(__name__)


@require_GET
def live(request):
    return JsonResponse({'ok': True})


@require_GET
def ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        check_media()
        if settings.MEDIA_WRITE_STATUS_FILE:
            status = json.loads(Path(settings.MEDIA_WRITE_STATUS_FILE).read_text())
            if not status['ok'] or not 0 <= time.time() - status['checked_at'] < 900:
                raise OSError('Media write probe failed or expired')
    except Exception:
        logger.exception('Readiness probe failed')
        return JsonResponse({'ok': False}, status=503)
    return JsonResponse({'ok': True})


@require_GET
def backup(request):
    try:
        status = json.loads(Path(settings.BACKUP_STATUS_FILE).read_text())
        ok = all(0 <= time.time() - status[key] < settings.BACKUP_MAX_AGE_SECONDS
                 for key in ('completed_at', 'source_created_at'))
    except (OSError, ValueError, KeyError):
        ok = False
    return JsonResponse({'ok': ok}, status=200 if ok else 503)


@require_GET
def core(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except Exception:
        return JsonResponse({'ok': False}, status=503)
    return JsonResponse({'ok': True})


@require_GET
def media(request):
    try:
        check_media()
    except Exception:
        return JsonResponse({'ok': False}, status=503)
    return JsonResponse({'ok': True})
