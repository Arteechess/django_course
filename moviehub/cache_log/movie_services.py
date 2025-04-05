from movies.models import Movie  # Импортируй свою модель Movie
from .models import MovieLog

def log_new_movies():
    recent_movies = Movie.objects.order_by('-created_at')[:10]  # последние 10
    for movie in recent_movies:
        if not MovieLog.objects.filter(movie_title=movie.title, created_at=movie.created_at).exists():
            MovieLog.objects.create(movie_title=movie.title, created_at=movie.created_at)
