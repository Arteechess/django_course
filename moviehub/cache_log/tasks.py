from celery import shared_task
from .services import save_log
from .movie_services import log_new_movies

@shared_task
def save_cache_log_task():
    save_log()

@shared_task
def log_new_movies_task():
    log_new_movies()
