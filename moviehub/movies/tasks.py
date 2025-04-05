from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from movies.models import Movie, User

@shared_task
def send_weekly_best_movies_email_task():
    # Получаем все фильмы (или можно отфильтровать по нужным критериям)
    movies = Movie.objects.all()
    subject = "Лучшие фильмы этой недели!"
    
    # Получаем всех пользователей
    users = User.objects.all()
    
    for user in users:
        # Генерация HTML сообщения
        html_message = render_to_string('weekly_best_movies.html', {'movies': movies, 'user': user})
        plain_message = strip_tags(html_message)  # Убираем HTML теги для обычного текста
        from_email = settings.EMAIL_HOST_USER  # Почта отправителя (обычно задается в настройках)
        to = user.email  # Получатель

        # Отправка письма
        send_mail(
            subject, 
            plain_message, 
            from_email, 
            [to], 
            html_message=html_message
        )
