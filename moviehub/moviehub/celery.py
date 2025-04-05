from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Устанавливаем настройки по умолчанию для Celery из Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviehub.settings')

app = Celery('moviehub')

# Используем настройки из Django для Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически ищем и регистрируем задачи в приложениях Django
app.autodiscover_tasks()
