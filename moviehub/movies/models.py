from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils import timezone  # Использование from django.utils import timezone
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.db.models import Avg
from django import template

register = template.Library()

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    groups = models.ManyToManyField(Group, related_name='custom_user_set', blank=True,)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions_set', blank=True,)

    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователи"

# Использование собственного модельного менеджера
class MovieManager(models.Manager):
    def recent_movies(self):
        return self.annotate(avg_score=Avg('ratings__score')).filter(avg_score__gt=7)


class Genre(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']  # Использование ordering в Meta
        verbose_name_plural = "Жанр"
        verbose_name = "Жанр"

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    release_date = models.DateField()
    genres = models.ManyToManyField(Genre, related_name='movies')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movies')
    poster = models.ImageField(upload_to='movie_posters/', blank=True, null=True) # Использование Pillow
    trailer_url = models.URLField(null=True, blank=True)
    trailer_file = models.FileField(upload_to='movie_trailers/', null=True, blank=True)
    history = HistoricalRecords()
    created_at = models.DateTimeField(default=timezone.now)
    objects = MovieManager()  # Подключение собственного менеджера

    class Meta:
        ordering = ['-release_date']  # Использование ordering в Meta
        verbose_name_plural = "Фильмы"
        verbose_name = "Фильмы"

    def get_absolute_url(self):
        return reverse('movie_detail', args=[self.id])  # Использование reverse и get_absolute_url

    def average_rating(self):
        return self.ratings.aggregate(Avg('score'))['score__avg'] or 0

    def __str__(self):
        return self.title


# Создание простого шаблонного тега
@register.filter
def capitalize_title(value):
    return value.title()

# Создание шаблонного тега с контекстными переменными
@register.filter
def short_description(value, length=100):
    return value[:length] + '...' if len(value) > length else value

# Шаблонный тег, возвращающий QuerySet
@register.simple_tag
def top_rated_movies():
    return Movie.objects.annotate(avg_score=Avg('ratings__score')).order_by('-avg_score')[:5] #функция агрегирования


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='favorited_by')
    added_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('user', 'movie')
        verbose_name_plural = "Любимые фильмы"
        verbose_name = "Любимые фильмы"

    def __str__(self):
        return f"Пользователь {self.user} добавил в избранное фильм {self.movie}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    score = models.IntegerField(choices=[(i, i) for i in range(1, 11)])  # Использование choices
    rated_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        unique_together = ('user', 'movie')
        verbose_name_plural = "Рейтинги"
        verbose_name = "Рейтинги"

    def __str__(self):
        return f"Пользователь {self.user} поставил оценку {self.score} на фильм {self.movie}"
