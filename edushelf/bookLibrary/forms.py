from django import forms
from .models import *


class EducationalInstitutionForm(forms.ModelForm):
    class Meta:
        model = EducationalInstitution
        fields = ['institution_name', 'contract_date', 'contract_duration']
        widgets = {
            'contract_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'institution_name': 'Название учебного заведения',
            'contract_date': 'Дата заключения договора',
            'contract_duration': 'Срок действия договора'
        }


class SpecialtiesForm(forms.ModelForm):
    class Meta:
        model = Specialties
        fields = '__all__'
        labels = {
            'specialty_name': 'Название специальности',
            'institution': 'Учебное заведение'
        }


class SubjectsForm(forms.ModelForm):
    class Meta:
        model = Subjects
        fields = '__all__'
        labels = {
            'subject_name': 'Название предмета'
        }

class SubjectSpecialtyLinkForm(forms.ModelForm):
    class Meta:
        model = SubjectSpecialtyLink
        fields = '__all__'
        labels = {
            'specialty': 'Специальность',
            'subject': 'Предмет',
            'course': 'Курс'
        }


class UserRolesForm(forms.ModelForm):
    class Meta:
        model = UserRoles
        fields = '__all__'
        labels = {
            'role_name': 'Название роли'
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'encrypted_email': 'Зашифрованная почта',
            'role': 'Роль',
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'is_active': 'Активный',
            'is_staff': 'Персонал',
            'is_superuser': 'Администратор',
            'last_login': 'Последний вход',
            'date_joined': 'Дата регистрации',
            'password': 'Пароль',
            'groups': 'Группы',
            'user_permissions': 'Права пользователя'
        }
        help_texts = {
            'username': 'Обязательное поле. Не более 150 символов. Только буквы, цифры и @/./+/-/_',
            'email': 'Электронная почта пользователя',
            'role': 'Роль пользователя в системе',
            'is_active': 'Указывает, следует ли считать этого пользователя активным',
            'is_staff': 'Определяет, может ли пользователь войти в административную панель',
            'is_superuser': 'Указывает, что пользователь имеет все права без явного назначения',
            'groups': 'Группы пользователей для назначения общих прав доступа. Пользователь получит все права, назначенные его группам.',
            'user_permissions': 'Индивидуальные права пользователя (рекомендуется использовать группы вместо отдельных прав)'
        }


class StudentsForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="Без пользователя" 
    )

    class Meta:
        model = Students
        fields = '__all__'
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'middle_name': 'Отчество',
            'email': 'Электронная почта',
            'status': 'Статус',
            'course': 'Курс',
            'specialty': 'Специальность',
            'user': 'Пользователь'
        }


class GenresForm(forms.ModelForm):
    class Meta:
        model = Genres
        fields = '__all__'
        labels = {
            'genre_name': 'Название жанра'
        }


class AuthorsForm(forms.ModelForm):
    class Meta:
        model = Authors
        fields = '__all__'
        labels = {
            'first_name': 'Имя автора',
            'last_name': 'Фамилия автора',
            'middle_name': 'Отчество автора (если есть)'
        }


class PublishersForm(forms.ModelForm):
    class Meta:
        model = Publishers
        fields = '__all__'
        labels = {
            'publisher_name': 'Название издательства'
        }


class BooksForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = '__all__'
        labels = {
            'book_title': 'Название книги',
            'author': 'Автор',
            'photo_book': 'Обложка книги',
            'book_file': 'Файл книги',
            'publication_year': 'Год издания',
            'page_count': 'Количество страниц',
            'genre': 'Жанр',
            'publisher': 'Издательство',
            'subject': 'Предмет'
        }


class NotesForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['note_content']
        labels = {
            'note_content': 'Создание заметки'
        } 

class BookmarksForm(forms.Form):
    class Meta:
        model = Bookmarks
        fields = '__all__'

class ReviewsForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ['rating', 'review_text']
        labels = {
            'rating': 'Рейтинг',
            'review_text': 'Текст отзыва'
        }

        def clean_rating(self):
            rating = self.cleaned_data.get('rating')
            if rating > 5:
                raise forms.ValidationError("Рейтинг не может быть больше 5.")
            return rating

class StatusForm(forms.ModelForm):
    class Meta:
        model = Status
        fields = '__all__'
        labels = {
            'status_name': 'Название статуса'
        }