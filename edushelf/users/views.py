from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from urllib.parse import quote
from bookLibrary.models import *
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                student = Students.objects.get(email=email)
            except Students.DoesNotExist:
                messages.error(request, 'Пользователь с таким email отсутствует в реестре студентов.')
                return render(request, 'users/register.html', {'form': form})
            user = form.save(commit=False)

            try:
                reader_role = UserRoles.objects.get(role_name='reader')
                user.role = reader_role
            except UserRoles.DoesNotExist:
                messages.error(request, 'Роль "reader" не найдена в системе.')
                return render(request, 'users/register.html', {'form': form})

            user.save()
            student.user = user
            try:
                registered_status = Status.objects.get(status_name='Зарегистрирован')
                student.status = registered_status
            except Status.DoesNotExist:
                messages.error(request, 'Статус "Зарегистрирован" не найден в системе.')
                return render(request, 'users/register.html', {'form': form})

            student.save()

            messages.success(request, f'Аккаунт {user.username} успешно создан!')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')

    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Ваш профиль успешно обновлен.')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    try:
        student = Students.objects.get(user=request.user)
    except Students.DoesNotExist:
        student = None

    context = {
        'u_form': u_form,
        'p_form': p_form,
        'student': student,
    }

    return render(request, 'users/profile.html', context)



class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.role.role_name == "reader":
            return reverse('bookLibrary:main_page')
        elif user.role.role_name == "bd_admin":
            return reverse('bookLibrary:bd_admin_page')
        elif user.role.role_name == "administrator":
            return reverse('bookLibrary:administrator_page')
        else:
            return reverse('bookLibrary:main_page')