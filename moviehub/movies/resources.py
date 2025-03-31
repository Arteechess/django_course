from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from .models import Movie, Genre

class MovieResource(resources.ModelResource):
    # Кастомизация поля: отображаем название жанров вместо ID
    genres = fields.Field(
        column_name='genres',
        attribute='genres',
        widget=ForeignKeyWidget(Genre, 'name'),
    )

    class Meta:
        model = Movie
        fields = ('id', 'title', 'description', 'release_date', 'genres', 'created_by')  # Поля для экспорта
        export_order = ('id', 'title', 'description', 'release_date', 'genres', 'created_by')  # Порядок полей

    # Кастомный метод для модификации данных (dehydrate)
    def dehydrate_title(self, movie):
        return f"{movie.title} (ID: {movie.id})"

    # Фильтрация данных для экспорта (get_export_queryset)
    def get_export_queryset(self, queryset, *args, **kwargs):
        return queryset.filter(release_date__gte="2020-01-01")  # Экспорт только фильмов после 2020 года

    # Пример дополнительной обработки данных
    def get_created_by(self, movie):
        return movie.created_by.username if movie.created_by else "Unknown"
