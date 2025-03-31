from django import forms
from .models import Movie
from django.contrib.auth.forms import UserCreationForm
from django import forms
from movies.models import User

class MovieForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        label="Описание",
        help_text="Введите краткое описание фильма.",
        error_messages={'required': "Описание обязательно для заполнения."}
    )

    class Meta:
        model = Movie
        fields = ['title', 'description', 'release_date', 'genres', 'poster']
        exclude = ['id']

        labels = {
            'title': 'Название',
            'release_date': 'Дата выхода',
            'genres': 'Жанры',
            'poster': 'Постер',
        }

        help_texts = {
            'title': 'Введите название фильма.',
            'release_date': 'Выберите дату выхода фильма.',
            'genres': 'Выберите один или несколько жанров.',
            'poster': 'Загрузите постер фильма.',
        }

        error_messages = {
            'title': {'required': "Название обязательно."},
            'release_date': {'required': "Дата выхода обязательна."},
            'genres': {'required': "Выберите хотя бы один жанр."},
            'poster': {'invalid': "Некорректный формат файла."},
        }

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'genres': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'poster': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if not title:
            raise forms.ValidationError('Название фильма не может быть пустым')
        return title

    class Media:
        css = {}
        js = ()


class CustomUserCreationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role']
