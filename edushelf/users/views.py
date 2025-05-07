from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from urllib.parse import quote
from bookLibrary.models import *
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from django.conf import settings


User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            
            # Проверка совпадения паролей
            if password1 != password2:
                messages.error(request, 'Пароли не совпадают.')
                return render(request, 'users/register.html', {'form': form})
            
            # Проверка сложности пароля
            if len(password1) < 8:
                messages.error(request, 'Пароль должен содержать минимум 8 символов.')
                return render(request, 'users/register.html', {'form': form})
            
            try:
                student = Students.objects.get(email=email)
            except Students.DoesNotExist:
                messages.error(request, 'Пользователь с таким email отсутствует в реестре студентов.')
                return render(request, 'users/register.html', {'form': form})
            
            # Проверка, не зарегистрирован ли уже пользователь с этим email
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Пользователь с таким email уже зарегистрирован.')
                return render(request, 'users/register.html', {'form': form})

            try:
                reader_role = UserRoles.objects.get(role_name='reader')
            except UserRoles.DoesNotExist:
                messages.error(request, 'Роль "reader" не найдена в системе. Обратитесь к администратору.')
                return render(request, 'users/register.html', {'form': form})

            try:
                registered_status = Status.objects.get(status_name='Зарегистрирован')
            except Status.DoesNotExist:
                messages.error(request, 'Статус "Зарегистрирован" не найден в системе. Обратитесь к администратору.')
                return render(request, 'users/register.html', {'form': form})

            try:
                user = form.save(commit=False)
                user.role = reader_role
                user.save()
                
                # Уведомление для нового пользователя
                Notification.objects.create(
                    user=user,
                    title="Добро пожаловать!",
                    message="Вы успешно зарегистрировались в системе как читатель."
                )
                
                student.user = user
                student.status = registered_status
                student.save()

                admins = User.objects.filter(role__role_name='administrator')
                for admin in admins:
                    Notification.objects.create(
                        user=admin,
                        title="Новая регистрация пользователя",
                        message=f"Зарегистрирован новый пользователь: {user.username} ({user.email})"
                    )
                
                messages.success(request, f'Аккаунт {user.username} успешно создан! Теперь вы можете войти.')
                return redirect('login')
                
            except Exception as e:
                messages.error(request, f'Произошла ошибка при регистрации: {str(e)}')
                return render(request, 'users/register.html', {'form': form})
                
        else:
            # Обработка ошибок валидации формы
            error_messages = {
                'username': {
                    'required': 'Имя пользователя обязательно для заполнения.',
                    'unique': 'Пользователь с таким именем уже существует.',
                    'invalid': 'Недопустимое имя пользователя.'
                },
                'email': {
                    'required': 'Email обязателен для заполнения.',
                    'invalid': 'Введите корректный email адрес.',
                    'unique': 'Пользователь с таким email уже зарегистрирован.'
                },
                'password1': {
                    'required': 'Пароль обязателен для заполнения.',
                    'min_length': 'Пароль должен содержать минимум 8 символов.',
                    'common': 'Пароль слишком простой.'
                },
                'password2': {
                    'required': 'Подтверждение пароля обязательно.',
                    'password_mismatch': 'Пароли не совпадают.'
                }
            }
            
            for field, errors in form.errors.items():
                for error in errors:
                    custom_message = error_messages.get(field, {}).get(error, error)
                    messages.error(request, f'{custom_message}')
    else:
        form = UserRegisterForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile(request):
    if request.user.role.role_name == 'administrator':
        template = 'bookLibrary/administrator/students/ListView.html'
    else:
        template = 'users/profile.html'

    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен.')
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
        'notifications': notifications,
    }

    return render(request, template, context)


@require_POST
@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('profile')

class CustomLoginView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        user = form.get_user()

        try:
            student = Students.objects.get(user=user)
            specialty = student.specialty
            institution = specialty.institution

            if institution.contract_date and institution.contract_duration:
                contract_end = institution.contract_date.replace(
                    year=institution.contract_date.year + institution.contract_duration
                )

                if date.today() > contract_end:
                    messages.error(self.request, "Ваш аккаунт заблокирован, обратитесь к администратору!")
                    return render(self.request, self.template_name, {'form': form})
        
        except Students.DoesNotExist:
            pass
        except Exception as e:
            messages.error(self.request, f"Ошибка при проверке договора: {str(e)}")
            return render(self.request, self.template_name, {'form': form})

        role_name = user.role.role_name.lower()
        welcome_message = f"Вы успешно вошли в систему как {role_name}."
        
        Notification.objects.create(
            user=user,
            title=f"Вход в систему ({role_name})",
            message=welcome_message
        )

        if user.role.role_name == "administrator":
            Notification.objects.create(
                user=user,
                title="Системные уведомления",
                message="Проверьте последние действия в системе."
            )

        return super().form_valid(form)

    def get_success_url(self):
        user = self.request.user
        if user.role.role_name == "reader":
            return reverse('bookLibrary:main_page')
        elif user.role.role_name == "bd_admin":
            return reverse('bookLibrary:bd_admin_page')
        elif user.role.role_name == "administrator":
            return reverse('bookLibrary:administrator_page')
        return reverse('bookLibrary:main_page')

    def form_invalid(self, form):
        messages.error(self.request, "Неверное имя пользователя или пароль.")
        return super().form_invalid(form)