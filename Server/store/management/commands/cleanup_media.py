import hashlib
import json
from pathlib import Path
import time
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from store.models import Product
from utils.remote_media import remote_request, object_route
from utils.write_lock import write_lock


class Command(BaseCommand):
    help = 'Move unreferenced N1 images to its recovery area; invalidate cached copies.'

    def handle(self, *args, **options):
        if not settings.MEDIA_ORIGIN_URL:
            return
        root = Path(settings.MEDIA_CLEANUP_DIR)
        processed = 0
        for path in sorted(root.glob('*.json')):
            record = json.loads(path.read_text())
            if record['due'] > time.time():
                continue
            processed += 1
            if processed > 100:
                break
            name = record['name']
            try:
                with write_lock():
                    if Product.objects.filter(image=name).exists():
                        path.unlink()
                        continue
                    response = remote_request('DELETE', object_route(name))
                    if response.status_code not in (204, 404):
                        raise OSError('Origin deletion failed')
                    if settings.MEDIA_CACHE_ROOT:
                        digest = hashlib.md5(('/media/' + name).encode()).hexdigest()
                        cached = Path(settings.MEDIA_CACHE_ROOT) / digest[-1] / digest[-3:-1] / digest
                        cached.unlink(missing_ok=True)
                    path.unlink()
            except Exception:
                self.stderr.write('Deferred cleanup will retry: ' + name)
