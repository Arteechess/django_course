from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import User, Genre, Movie, Favorite, Rating
from .serializers import UserSerializer, GenreSerializer, MovieSerializer, FavoriteSerializer, RatingSerializer
from rest_framework.generics import ListAPIView, get_object_or_404  # Использование get_object_or_404
from django.db.models import Q
from .pagination import CustomPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Movie
from .forms import CustomUserCreationForm, MovieForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.contrib import messages
from django.http import HttpResponseRedirect  # Добавлено: HttpResponseRedirect для редиректов
from django.db.models import Avg


def movies_list(request):
    # Поиск по названию (поиск с учетом регистра)
    search_term = request.GET.get('search', '')

     # Извлекаем все фильмы с их жанрами, пользователями, создавшими фильмы, и пользователями, добавившими фильм в избранное
    movies = Movie.objects.select_related('created_by')\
                        .prefetch_related('genres', 'favorited_by')\
                        .all()

    # Фильтруем фильмы по названию, если строка поиска не пуста
    if search_term:
        movies = Movie.objects.filter(title__icontains=search_term)

    movie_count = Movie.objects.count()

    # Топ 5 фильмов (по средней оценке)
    top_movies = Movie.objects.annotate(avg_score=Avg('ratings__score')).order_by('-avg_score')[:5]

    # Получаем только названия фильмов (с использованием values)
    movie_titles = Movie.objects.values('title')

    # Получаем список названий фильмов (с использованием values_list)
    movie_titles_list = Movie.objects.values_list('title', flat=True)

    # Передаем данные в контекст
    context = {
        'movies': movies,
        'movie_count': movie_count,
        'top_movies': top_movies,
        'movie_titles': movie_titles,
        'movie_titles_list': movie_titles_list,
        'search_term': search_term, 
    }

    return render(request, 'movies_list.html', context)

def movie_detail(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    return render(request, 'movie_detail.html', {'movie': movie})

def movie_create(request):
    if request.method == 'POST':
        form = MovieForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            # Извлекаем данные из cleaned_data
            title = cleaned_data.get('title')
            description = cleaned_data.get('description')
            release_date = cleaned_data.get('release_date')
            genres = cleaned_data.get('genres')
            poster = cleaned_data.get('poster')

            movie = form.save(commit=False)  # Не сохраняем сразу, чтобы установить created_by
            movie.created_by = request.user  # Устанавливаем текущего пользователя
            movie.save()  # Сохраняем фильм

            print(f'Фильм создан: {title}, {description}, {release_date}, {genres}, {poster}')

            # Сохранить ID фильма в сессии
            request.session['last_movie_id'] = movie.id
            
            return redirect(movie.get_absolute_url())
    else:
        form = MovieForm()
    
    return render(request, 'movie_form.html', {'form': form})

def movie_update(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        form = MovieForm(request.POST, request.FILES, instance=movie)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/')  # Добавлено: HttpResponseRedirect для редиректа
    else:
        form = MovieForm(instance=movie)
    return render(request, 'movie_form.html', {'form': form})

def movie_delete(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    if request.method == "POST":
        movie.delete()
        return HttpResponseRedirect('/')  # Добавлено: HttpResponseRedirect для редиректа
    return render(request, 'movie_confirm_delete.html', {'movie': movie})


# Представление для страницы регистрации
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Автоматический вход после регистрации
            return redirect('movies_list')  # Перенаправление на главную страницу
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

# Использование встроенных вьюшек для входа и выхода
class CustomLoginView(LoginView):
    template_name = 'login.html'  # Укажите свой шаблон для страницы логина

def custom_logout(request):
    logout(request)
    messages.info(request, "Вы успешно вышли из системы.")  # Добавляем сообщение о выходе
    return redirect('movies_list')  # Перенаправление на главную страницу


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['release_date', 'created_by', 'genres__name']
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'title']
    pagination_class = CustomPagination  # Пагинация с try-except

    def get_queryset(self):
        queryset = super().get_queryset()
        try:
            return queryset.filter(release_date__gte='2000-01-01').exclude(genres__name='Comedy').order_by('-release_date')  # Использование exclude и order_by
        except Exception as e:
            return queryset.none()

    @action(methods=['GET'], detail=False)
    def filter_by_genre(self, request):
        genre_name = request.query_params.get('genre', None)
        if not genre_name:
            return Response({"error": "Genre parameter is required."}, status=400)
        movies = Movie.objects.filter(Q(genres__name__icontains=genre_name)).distinct()  # Использование __
        serializer = MovieSerializer(movies, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def add_to_favorites(self, request, pk=None):
        user = request.user
        movie = get_object_or_404(Movie, pk=pk)  # Использование get_object_or_404
        if Favorite.objects.filter(user=user, movie=movie).exists():
            return Response({"error": "Movie is already in favorites."}, status=400)
        favorite = Favorite.objects.create(user=user, movie=movie)
        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=201)


class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FilteredMoviesView(ListAPIView):
    serializer_class = MovieSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Movie.objects.filter(
            (Q(genres__name="Action") | Q(genres__name="Adventure")) &
            Q(release_date__gt="2020-01-01") &
            ~Q(created_by__role="admin")  # Использование ~Q
        ).distinct()


class FilteredFavoritesView(ListAPIView):
    serializer_class = FavoriteSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Favorite.objects.filter(
            (Q(user_id=2) | Q(movie__ratings__score__gt=4)) &
            Q(movie__genres__name="Drama") &
            ~Q(movie__title__icontains="Horror")  # Использование ~Q и __
        ).distinct()
