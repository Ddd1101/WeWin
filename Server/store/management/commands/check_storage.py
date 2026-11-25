import json
import os
import tempfile
import time
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from utils.media import check_media
from utils.write_lock import write_lock


class Command(BaseCommand):
    help = 'Verify media read/write/rename/delete as the application user.'

    def handle(self, *args, **options):
        ok = False
        skipped = False
        original = renamed = None
        try:
            with write_lock():
                check_media()
                try:
                    with tempfile.NamedTemporaryFile(dir=settings.MEDIA_ROOT, prefix='.write-probe-', delete=False) as target:
                        original = Path(target.name)
                        target.write(b'wewin-media-write-probe')
                        target.flush()
                        os.fsync(target.fileno())
                    renamed = original.with_suffix('.renamed')
                    original.rename(renamed)
                    if renamed.read_bytes() != b'wewin-media-write-probe':
                        raise OSError('Write probe content mismatch')
                    renamed.unlink()
                    ok = True
                finally:
                    for path in (original, renamed):
                        if path and path.exists():
                            path.unlink()
        except BlockingIOError:
            skipped = True
            self.stdout.write('Backup active; retry storage probe on next tick')
            return
        finally:
            if settings.MEDIA_WRITE_STATUS_FILE and not skipped:
                status = Path(settings.MEDIA_WRITE_STATUS_FILE)
                temporary = status.with_suffix('.tmp')
                temporary.write_text(json.dumps({'ok': ok, 'checked_at': time.time()}))
                temporary.replace(status)
        if not ok:
            raise CommandError('Media write probe failed')
        self.stdout.write('Media read/write/rename/delete passed')
