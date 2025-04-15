from django import forms
from .models import *


class EducationalInstitutionForm(forms.ModelForm):
    class Meta:
        model = EducationalInstitution
        fields = ['institution_name', 'contract_date', 'contract_duration']
        widgets = {
            'contract_date': forms.DateInput(attrs={'type': 'date'}),
        }


class SpecialtiesForm(forms.ModelForm):
    class Meta:
        model = Specialties
        fields = '__all__'


class SubjectsForm(forms.ModelForm):
    class Meta:
        model = Subjects
        fields = '__all__'

class SubjectSpecialtyLinkForm(forms.ModelForm):
    class Meta:
        model = SubjectSpecialtyLink
        fields = '__all__'


class UserRolesForm(forms.ModelForm):
    class Meta:
        model = UserRoles
        fields = '__all__'


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'


class StudentsForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        empty_label="Без пользователя" 
    )

    class Meta:
        model = Students
        fields = '__all__'


class GenresForm(forms.ModelForm):
    class Meta:
        model = Genres
        fields = '__all__'


class AuthorsForm(forms.ModelForm):
    class Meta:
        model = Authors
        fields = '__all__'


class PublishersForm(forms.ModelForm):
    class Meta:
        model = Publishers
        fields = '__all__'


class BooksForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = '__all__'


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