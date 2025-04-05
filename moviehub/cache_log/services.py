from django.core.cache import cache
from .models import VisitLog

def log_to_cache(data):
    key = f"log_{data['date'].timestamp()}"
    cache.set(key, data, timeout=60 * 60)

def save_log():
    keys = cache.keys("log_*")
    for key in keys:
        data = cache.get(key)
        if data:
            VisitLog.objects.create(**data)
            cache.delete(key)
