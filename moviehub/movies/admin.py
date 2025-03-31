from django.contrib import admin
from django.utils.html import format_html
from .models import User, Genre, Movie, Favorite, Rating
from import_export.admin import ExportMixin
from .resources import MovieResource
from simple_history.admin import SimpleHistoryAdmin
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.core.files.storage import default_storage
import os


class GenreInline(admin.TabularInline):  # Встроенные жанры для фильма
    model = Movie.genres.through  # Отображаем связь M2M
    extra = 1  # Показываем одну пустую строку для добавления нового жанра


class FavoriteInline(admin.TabularInline):  # Встроенные избранные для фильма
    model = Favorite
    extra = 0
    fields = ('user',)
    readonly_fields = ('user',)


class MovieAdmin(ExportMixin, SimpleHistoryAdmin, admin.ModelAdmin):
    resource_class = MovieResource  # Подключаем ресурс для экспорта
    list_display = ('id', 'title', 'release_date', 'created_by_link', 'genre_list', 'average_rating', 'poster_preview', 'recent_movie', 'trailer_url', 'trailer_file')  
    list_display_links = ('title',)  # Гиперссылка на редактирование фильма
    search_fields = ('title', 'description')  # Поиск по названию и описанию
    list_filter = ('release_date', 'genres')  # Фильтры по дате выхода и жанрам
    ordering = ('-release_date',)  # Сортировка по дате выхода (по убыванию)
    readonly_fields = ('created_by', 'poster_preview')
    date_hierarchy = 'release_date'  # Добавление date_hierarchy
    raw_id_fields = ('created_by',)  # Оптимизация поиска пользователя
    filter_horizontal = ('genres',)

    inlines = [GenreInline, FavoriteInline]  # Инлайнов

    fieldsets = (
        ("Основная информация", {
            'fields': ('title', 'description', 'release_date', 'created_by', 'poster', 'poster_preview', 'trailer_url', 'trailer_file')
        }),
        ("Связи и доп. информация", {
            'fields': ('genres',),  # Тут будет поле для выбора жанров через меню
        }),
    )

    @admin.display(description="Создатель")
    def created_by_link(self, obj):
        if obj.created_by:
            url = f"/admin/movies/user/{obj.created_by.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.created_by.username)
        return "Не указано"

    @admin.display(description="Жанры")
    def genre_list(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])

    @admin.display(description="Превью постера")
    def poster_preview(self, obj):
        if obj.poster:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.poster.url)
        return "Нет постера"

    @admin.display(description="Высокий рейтинг фильма")
    def recent_movie(self, obj):
        return "Да" if obj.average_rating() > 7 else "Нет"

    def generate_pdf(self, request, queryset):
        """Генерация PDF отчета"""
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="movies_report.pdf"'
        p = canvas.Canvas(response, pagesize=letter)
        width, height = letter
        p.setFont("Helvetica", 16)
        p.drawString(100, height - 100, "Movies Report")
        y_position = height - 150

        for movie in queryset:
            p.setFont("Helvetica", 12)
            title = str(movie.title) if movie.title else "No Title Available"
            p.drawString(100, y_position, f"Title: {title}")
            y_position -= 20
            release_date = movie.release_date.strftime('%Y-%m-%d') if movie.release_date else "No Release Date"
            p.drawString(100, y_position, f"Release Date: {release_date}")
            y_position -= 20
            description = str(movie.description) if movie.description else "No Description Available"
            p.drawString(100, y_position, f"Description: {description}")
            y_position -= 40

            genres = ", ".join([genre.name for genre in movie.genres.all()]) if movie.genres.exists() else "No Genres Available"
            p.drawString(100, y_position, f"Genres: {genres}")
            y_position -= 20

            if movie.poster:
                poster_path = default_storage.path(movie.poster.name)
                if os.path.exists(poster_path):
                    try:
                        p.drawImage(poster_path, 100, y_position - 100, width=100, height=150)
                        y_position -= 180
                    except Exception as e:
                        p.drawString(100, y_position, f"Ошибка загрузки изображения: {str(e)}")
                        y_position -= 20
                else:
                    p.drawString(100, y_position, "Poster's file not found")
                    y_position -= 20
            else:
                p.drawString(100, y_position, "No Poster Available")
                y_position -= 20

            avg_rating = movie.average_rating()
            p.drawString(100, y_position, f"Average Rating: {avg_rating}")
            y_position -= 40

        p.showPage()
        p.save()

        return response

    generate_pdf.short_description = "Сгенерировать PDF отчет"
    actions = [generate_pdf]

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ('id', 'user_link', 'movie_link', 'added_at')
    search_fields = ('user__username', 'movie__title')
    ordering = ('-added_at',)

    @admin.display(description="Пользователь")
    def user_link(self, obj):
        if obj.user:
            url = f"/admin/movies/user/{obj.user.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "Не указано"

    @admin.display(description="Фильм")
    def movie_link(self, obj):
        if obj.movie:
            url = f"/admin/movies/movie/{obj.movie.id}/change/"
            return format_html('<a href="{}">{}</a>', url, obj.movie.title)
        return "Не указано"


@admin.register(Rating)
class RatingAdmin(SimpleHistoryAdmin, admin.ModelAdmin):
    list_display = ('id', 'user', 'movie', 'score', 'rated_at')
    search_fields = ('user__username', 'movie__title')
    ordering = ('-rated_at',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'role', 'is_active', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('role', 'is_active', 'is_staff')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions')


admin.site.register(Movie, MovieAdmin)
