from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from movies import views
import debug_toolbar
from rest_framework.routers import DefaultRouter

from movies.views import (
    UserViewSet, GenreViewSet, MovieViewSet, FavoriteViewSet, RatingViewSet, 
    FilteredMoviesView, FilteredFavoritesView
)

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="MovieHub API",
        default_version='v1',
        description="Документация API для MovieHub",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your@email.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Настройка роутера для API
router = DefaultRouter()
router.register('users', UserViewSet)
router.register('genres', GenreViewSet)
router.register('movies', MovieViewSet, basename='movie')
router.register('favorites', FavoriteViewSet)
router.register('ratings', RatingViewSet)

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    
    # API маршруты
    path('api/', include(router.urls)),
    path('api/filtered-movies/', FilteredMoviesView.as_view(), name='filtered-movies'),
    path('api/filtered-favorites/', FilteredFavoritesView.as_view(), name='filtered-favorites'),

    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.custom_logout, name='logout'),

    # Маршруты для HTML-страниц
    path('', views.movies_list, name='movies_list'),  # Главная страница со списком фильмов
    path('movies/<int:pk>/', views.movie_detail, name='movie_detail'),  # Страница фильма
    path('movies/create/', views.movie_create, name='movie_create'),  # Форма создания фильма
    path('movies/<int:pk>/edit/', views.movie_update, name='movie_update'),  # Форма редактирования фильма
    path('movies/<int:pk>/delete/', views.movie_delete, name='movie_delete'),  # Удаление фильма

    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('__debug__/', include(debug_toolbar.urls)),
]

# Добавление маршрутов для работы со статикой и медиафайлами
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
