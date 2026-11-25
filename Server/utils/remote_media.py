"""Bounded network operations to the N1 origin; never silently write locally."""
import hashlib
from pathlib import Path
from urllib.parse import quote
import requests
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousFileOperation
from .media import StorageUnavailable, validate_image


def remote_request(method, route, **kwargs):
    token = settings.MEDIA_ORIGIN_READ_TOKEN if method in ('GET', 'HEAD') else settings.MEDIA_ORIGIN_WRITE_TOKEN
    headers = kwargs.pop('headers', {})
    headers['Authorization'] = 'Bearer ' + token
    try:
        with requests.Session() as session:
            session.trust_env = False
            response = session.request(method, settings.MEDIA_ORIGIN_URL + route, headers=headers,
                                       timeout=(3, 120 if method == 'PUT' else 5), **kwargs)
        if response.status_code not in (200, 201, 204, 404):
            raise StorageUnavailable('媒体服务请求失败')
        return response
    except requests.RequestException as exc:
        raise StorageUnavailable('N1 图片服务不可用') from exc


def object_route(name):
    path = Path(name)
    if not name.startswith('products/') or path.is_absolute() or '..' in path.parts or '\\' in name:
        raise SuspiciousFileOperation('Invalid media key')
    return '/objects/' + quote(name, safe='/')


class N1ImageStorage(FileSystemStorage):
    def _save(self, name, content):
        from .media import queue_cleanup
        validate_image(content)
        content.seek(0)
        h = hashlib.sha256()
        for chunk in content.chunks():
            h.update(chunk)
        content.seek(0)
        # Track before transmission: a lost response may mean the origin committed.
        queue_cleanup(name, 'orphan', delay=86400)
        response = remote_request('PUT', object_route(name), data=content,
                                  headers={'X-Content-SHA256': h.hexdigest(), 'Content-Length': str(content.size)})
        if response.status_code not in (200, 201) or response.json().get('sha256') != h.hexdigest():
            raise StorageUnavailable('媒体校验失败')
        return name

    def exists(self, name):
        return remote_request('HEAD', object_route(name)).status_code == 200

    def size(self, name):
        response = remote_request('HEAD', object_route(name))
        if response.status_code == 404:
            raise FileNotFoundError(name)
        return int(response.headers['Content-Length'])

    def delete(self, name):
        from .media import queue_cleanup
        queue_cleanup(name, 'obsolete')

    def path(self, name):
        raise NotImplementedError('N1 media has no local path')

    def _open(self, name, mode='rb'):
        raise NotImplementedError('Use the HTTPS media URL to read N1 media')
