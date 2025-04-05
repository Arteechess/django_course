import json
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from .services import log_to_cache

EXCLUDE_PATHS = ['/admin/', '/login/']

def get_ip_address(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')

class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if any(request.path.startswith(path) for path in EXCLUDE_PATHS):
            return None
        data = {
            'user': request.user.username if request.user.is_authenticated else None,
            'date': datetime.now(),
            'url': request.path,
            'method': request.method,
            'get_params': json.dumps(request.GET.dict()),
            'post_params': json.dumps(request.POST.dict()),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': get_ip_address(request),
        }
        log_to_cache(data)
