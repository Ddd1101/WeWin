"""Coordinate API/scheduler writes with a consistent database + media backup."""
from contextlib import contextmanager
from django.conf import settings


@contextmanager
def write_lock():
    if not settings.WRITE_LOCK_FILE:
        yield
        return
    import fcntl
    with open(settings.WRITE_LOCK_FILE, 'a') as lock:
        fcntl.flock(lock, fcntl.LOCK_SH | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)
