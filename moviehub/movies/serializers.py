from rest_framework import serializers
from .models import User, Genre, Movie, Favorite, Rating


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']


class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)

    class Meta:
        model = Movie
        fields = ['id', 'title', 'description', 'release_date', 'genres', 'created_by']


class FavoriteSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    movie_poster = serializers.SerializerMethodField()
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'user', 'user_username', 'movie', 'movie_title', 'movie_poster', 'comment', 'added_at']
        read_only_fields = ['user', 'added_at']

    def get_movie_poster(self, obj):
        if obj.movie.poster:
            return obj.movie.poster.url
        return None


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'user', 'movie', 'score', 'rated_at']
