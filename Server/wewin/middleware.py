import logging
from django.db import OperationalError, InterfaceError, connection
from django.http import JsonResponse
from utils.write_lock import write_lock

logger = logging.getLogger(__name__)


class AvailabilityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(('/api/', '/admin/')):
            return self.get_response(request)
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
            # Admin login and all API mutations share the backup barrier.
            with write_lock():
                return self.get_response(request)
        except (OperationalError, InterfaceError, BlockingIOError):
            logger.exception('Database unavailable or backup write barrier active')
            response = JsonResponse({'error': '服务暂不可用，请稍后重试'}, status=503)
            response['Retry-After'] = '5'
            return response

    def process_exception(self, request, exception):
        if isinstance(exception, (OperationalError, InterfaceError)):
            logger.error('Database request failed', exc_info=exception)
            return JsonResponse({'error': '数据库暂不可用'}, status=503)
