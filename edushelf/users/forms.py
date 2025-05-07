from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile
from django.utils.translation import gettext_lazy as _


User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(label='Электронная почта', required=True)
    username = forms.CharField(label='Логин', max_length=150)
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Имя пользователя',
            'email': 'Email',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля'
        }
        help_texts = {
            'username': 'Только буквы, цифры и @/./+/-/_',
            'password1': 'Минимум 8 символов'
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(label='E-mail')
    first_name = forms.CharField(label='Имя', required=False)
    last_name = forms.CharField(label='Фамилия', required=False)
    middle_name = forms.CharField(label='Отчество', required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'middle_name']
        labels = {
            'username': 'Логин',
        }

class ProfileUpdateForm(forms.ModelForm):
    image = forms.ImageField(label='Фото', required=False, widget=forms.FileInput)

    class Meta:
        model = Profile
        fields = ['image']


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Имя пользователя', max_length=254)
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)