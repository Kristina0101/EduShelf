import json
from django.forms import ValidationError
from django.shortcuts import render, get_object_or_404, redirect

from .models import *
from django.urls import *
from django.core.paginator import Paginator
import fitz 
from django.db.models import Q
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import *
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.contrib import messages
import subprocess
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
BASE_DIR = settings.BASE_DIR
# Create your views here.
def main_page(request):
    books_list = Books.objects.all()
    paginator = Paginator(books_list, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    
    return render(request, 'bookLibrary/main_page.html', {'books': books})



@login_required(login_url="login")
def description_book(request, id):
    book = get_object_or_404(Books, pk=id)

    pdf_path = book.book_file.path
    doc = fitz.open(pdf_path)
    total_pages = doc.page_count

    page_number = int(request.GET.get("page", 1))
    page_number = max(1, min(page_number, total_pages))

    if request.method == "POST" and "add_note" in request.POST:
        if request.user.is_authenticated:
            note_form = NotesForm(request.POST)
            if note_form.is_valid():
                note = note_form.save(commit=False)
                note.book = book
                note.page_number = page_number
                note.user = request.user
                note.save()
                messages.success(request, "Заметка успешно добавлена!")
                return redirect("bookLibrary:description_book", id=book.book_id)
        else:
            messages.error(request, "Вы должны войти в систему, чтобы добавить заметку.")
            return redirect("login")

    if request.method == "POST" and "add_review" in request.POST:
        review_form = ReviewsForm(request.POST)
        if review_form.is_valid():
            rating = review_form.cleaned_data.get("rating")
            if rating > 5:
                messages.error(request, "Рейтинг не может быть больше 5.")
            elif rating < 1:
                messages.error(request, "Рейтинг не может быть меньше 1.")
            else:
                review = review_form.save(commit=False)
                review.book = book
                review.user = request.user
                review.save()
                messages.success(request, "Отзыв успешно добавлен!")
                return redirect("bookLibrary:description_book", id=book.book_id)

    notes = Notes.objects.filter(book=book, user=request.user)
    reviews = Reviews.objects.filter(book=book)
    bookmarks = Bookmarks.objects.filter(book=book, user=request.user)

    context = {
        "book": book,
        "page_number": page_number,
        "total_pages": total_pages,
        "notes": notes,
        "reviews": reviews,
        "bookmarks": bookmarks,
        "note_form": NotesForm(),
        "review_form": ReviewsForm(),
    }
    return render(request, "bookLibrary/description_book.html", context)
@login_required(login_url="login")
def delete_note(request, note_id):
    note = get_object_or_404(Notes, note_id=note_id)
    if note.user == request.user:
        note.delete()
        messages.success(request, "Заметка удалена.")
    return redirect("bookLibrary:description_book", id=note.book.book_id)

@login_required(login_url="login")
def delete_review(request, review_id):
    review = get_object_or_404(Reviews, review_id=review_id)
    if review.user == request.user:
        review.delete()
        messages.success(request, "Отзыв удален.")
    return redirect("bookLibrary:description_book", id=review.book.book_id)

def delete_note(request, note_id):
    note = get_object_or_404(Notes, note_id=note_id)
    if note.user == request.user:
        note.delete()
    return redirect("bookLibrary:description_book", id=note.book.book_id)

def delete_review(request, review_id):
    review = get_object_or_404(Reviews, review_id=review_id)
    if review.user == request.user:
        review.delete()
    return redirect("bookLibrary:description_book", id=review.book.book_id)


@require_POST
@csrf_exempt
@login_required
def add_bookmark(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    data = json.loads(request.body)
    page_number = data.get('page_number')
    
    existing_bookmark = Bookmarks.objects.filter(
        book=book, 
        user=request.user, 
        page_number=page_number
    ).exists()
    
    if existing_bookmark:
        return JsonResponse({
            'success': False,
            'message': 'Закладка на этой странице уже существует'
        })
    
    bookmark = Bookmarks.objects.create(
        book=book,
        user=request.user,
        page_number=page_number
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Закладка успешно добавлена'
    })

@login_required
def delete_bookmark(request, bookmark_id):
    bookmark = get_object_or_404(Bookmarks, pk=bookmark_id, user=request.user)
    bookmark.delete()
    messages.success(request, "Закладка удалена!")
    return redirect("bookLibrary:description_book", id=bookmark.book.book_id)


def catalog(request):
    geners = Genres.objects.all()
    subjects = Subjects.objects.all()

    selected_genre = request.GET.get('genre')
    selected_subject = request.GET.get('subject')
    search_query = request.GET.get('search', '')
    sort_field = request.GET.get('sort', 'title_asc')

    books_list = Books.objects.select_related('author', 'genre', 'subject')

    if selected_genre:
        books_list = books_list.filter(genre__genre_id=selected_genre)
    if selected_subject:
        books_list = books_list.filter(subject__subject_id=selected_subject)

    if search_query:
        books_list = books_list.filter(
            Q(book_title__icontains=search_query) |
            Q(author__first_name__icontains=search_query) |
            Q(author__last_name__icontains=search_query)
        )

    if sort_field == 'title_desc':
        books_list = books_list.order_by('-book_title')
    elif sort_field == 'author_asc':
        books_list = books_list.order_by('author__last_name', 'author__first_name')
    elif sort_field == 'author_desc':
        books_list = books_list.order_by('-author__last_name', '-author__first_name')
    else:
        books_list = books_list.order_by('book_title')

    paginator = Paginator(books_list, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)

    return render(
        request,
        'bookLibrary/catalog.html',
        {
            'books': books,
            'geners': geners,
            'subjects': subjects,
            'selected_genre': selected_genre,
            'selected_subject': selected_subject,
            'search_query': search_query,
            'sort_field': sort_field,
        }
    )




def bd_admin_page(request):
    return render(request, 'bookLibrary/bd_admin/bd_admin_page.html')

def statistic(request):
    # Общая статистика
    total_users = User.objects.count()
    registered_students = Students.objects.filter(user__isnull=False).count()
    total_bookmarks = Bookmarks.objects.count()
    total_notes = Notes.objects.count()
    total_reviews = Reviews.objects.count()

    # Статистика регистрации
    last_7_days = now() - timedelta(days=7)
    user_registration_stats = User.objects.filter(
        date_joined__gte=last_7_days
    ).extra({'day': "date(date_joined)"}).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    # Статистика авторизаций
    login_stats = User.objects.filter(
        last_login__gte=last_7_days
    ).extra({'day': "date(last_login)"}).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    # Уникальные пользователи за последние 7 дней
    active_users_7days = User.objects.filter(
        last_login__gte=last_7_days
    ).distinct().count()

    context = {
        'total_users': total_users,
        'registered_students': registered_students,
        'total_bookmarks': total_bookmarks,
        'total_notes': total_notes,
        'total_reviews': total_reviews,
        'user_registration_stats': user_registration_stats,
        'login_stats': login_stats,
        'active_users_7days': active_users_7days,
        'total_active_users': User.objects.exclude(last_login__isnull=True).count(),
    }
    return render(request, 'bookLibrary/administrator/statistic.html', context)


def log_view(request):
    log_path = os.path.join(settings.BASE_DIR, 'logs', 'app.log')
    try:
        # Пробуем несколько кодировок по очереди
        encodings = ['utf-8', 'cp1251', 'utf-16', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(log_path, 'r', encoding=encoding) as f:
                    log_content = f.read().splitlines()[-100:]  # Последние 100 строк
                break
            except UnicodeDecodeError:
                continue
        else:
            log_content = ["Не удалось прочитать лог-файл (проблема с кодировкой)"]
            
    except Exception as e:
        log_content = [f"Ошибка при чтении лог-файла: {str(e)}"]
    
    context = {
        'log_content': log_content,
        'log_file': log_path
    }
    return render(request, 'bookLibrary/bd_admin/logs.html', context)

class StudentsListView(ListView):
    model = Students
    template_name = 'bookLibrary/bd_admin/students/ListView.html'
    context_object_name = 'StudentsListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        StudentsListView = paginator.get_page(page)
        context['StudentsListView'] = StudentsListView
        return context


class StudentsCreateView(CreateView):
    model = Students
    form_class = StudentsForm
    template_name = 'bookLibrary/bd_admin/students/CreateView.html'
    context_object_name = 'StudentsCreateView'
    success_url = reverse_lazy('bookLibrary:StudentsListView')

class StudentsDetailView(DetailView):
    model = Students
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/bd_admin/students/DetailView.html'
    context_object_name = 'StudentsListView'

class StudentsUpdateView(UpdateView):
    model = Students
    form_class = StudentsForm
    pk_url_kwarg = 'pk'
    context_object_name = 'StudentsUpdateView'
    template_name = 'bookLibrary/bd_admin/students/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:StudentsListView')

class StudentsDeleteView(DeleteView):
    model = Students
    context_object_name = 'StudentsDeleteView'
    template_name = 'bookLibrary/bd_admin/students/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:StudentsListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['student'] = get_object_or_404(Students, pk=self.kwargs['pk'])
        return context
    

class UsersListView(ListView):
    model = User
    template_name = 'bookLibrary/bd_admin/users/ListView.html'
    context_object_name = 'UsersListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        UsersListView = paginator.get_page(page)
        context['UsersListView'] = UsersListView
        return context


class UsersCreateView(CreateView):
    model = User
    form_class = UserForm
    template_name = 'bookLibrary/bd_admin/users/CreateView.html'
    context_object_name = 'UsersCreateView'
    success_url = reverse_lazy('bookLibrary:UsersListView')

class UsersDetailView(DetailView):
    model = User
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/bd_admin/users/DetailView.html'
    context_object_name = 'UsersListView'

class UsersUpdateView(UpdateView):
    model = User
    form_class = UserForm
    pk_url_kwarg = 'pk'
    context_object_name = 'UsersUpdateView'
    template_name = 'bookLibrary/bd_admin/users/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:UsersListView')

class UsersDeleteView(DeleteView):
    model = User
    context_object_name = 'UsersDeleteView'
    template_name = 'bookLibrary/bd_admin/users/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:UsersListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['user'] = get_object_or_404(User, pk=self.kwargs['pk'])
        return context
    
class StudentsListView(ListView):
    model = Students
    template_name = 'bookLibrary/bd_admin/students/ListView.html'
    context_object_name = 'StudentsListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        StudentsListView = paginator.get_page(page)
        context['StudentsListView'] = StudentsListView
        return context


class StudentsCreateView(CreateView):
    model = Students
    form_class = StudentsForm
    template_name = 'bookLibrary/bd_admin/students/CreateView.html'
    context_object_name = 'StudentsCreateView'
    success_url = reverse_lazy('bookLibrary:StudentsListView')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Студент успешно добавлен!')
            return response
        except ValidationError as e:
            messages.error(self.request, f'Ошибка валидации: {", ".join(e.messages)}')
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Ошибка при добавлении студента: {str(e)}')
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        error_messages = {
            'email': {
                'unique': 'Студент с таким email уже существует.',
                'invalid': 'Введите корректный email адрес.'
            },
            'student_id': {
                'unique': 'Студент с таким номером уже существует.'
            }
        }
        
        for field, errors in form.errors.items():
            for error in errors:
                custom_message = error_messages.get(field, {}).get(error, error)
                messages.error(self.request, f'{field}: {custom_message}')
        return super().form_invalid(form)

class StudentsDetailView(DetailView):
    model = Students
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/bd_admin/students/DetailView.html'
    context_object_name = 'StudentsListView'

    def get(self, request, *args, **kwargs):
        try:
            return super().get(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f'Ошибка при загрузке данных студента: {str(e)}')
            return redirect('bookLibrary:StudentsListView')

class StudentsUpdateView(UpdateView):
    model = Students
    form_class = StudentsForm
    pk_url_kwarg = 'pk'
    context_object_name = 'StudentsUpdateView'
    template_name = 'bookLibrary/bd_admin/students/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:StudentsListView')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Данные студента успешно обновлены!')
            return response
        except ValidationError as e:
            messages.error(self.request, f'Ошибка валидации: {", ".join(e.messages)}')
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f'Ошибка при обновлении данных: {str(e)}')
            return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Ошибка в поле {field}: {error}')
        return super().form_invalid(form)

class StudentsDeleteView(DeleteView):
    model = Students
    context_object_name = 'StudentsDeleteView'
    template_name = 'bookLibrary/bd_admin/students/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:StudentsListView')
    success_message = "Студент успешно удалён"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['student'] = get_object_or_404(Students, pk=self.kwargs['pk'])
        return context

    def delete(self, request, *args, **kwargs):
        try:
            student = self.get_object()
            student_name = f"{student.last_name} {student.first_name}"
            response = super().delete(request, *args, **kwargs)
            messages.success(request, f'Студент {student_name} успешно удалён!')
            return response
        except Exception as e:
            messages.error(request, f'Ошибка при удалении студента: {str(e)}')
            return redirect(self.success_url)
    

class RolesListView(ListView):
    model = UserRoles
    template_name = 'bookLibrary/bd_admin/roles/ListView.html'
    context_object_name = 'RolesListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        RolesListView = paginator.get_page(page)
        context['RolesListView'] = RolesListView
        return context


class RolesCreateView(CreateView):
    model = UserRoles
    form_class = UserRolesForm
    template_name = 'bookLibrary/bd_admin/roles/CreateView.html'
    context_object_name = 'RolesCreateView'
    success_url = reverse_lazy('bookLibrary:RolesListView')

class RolesDetailView(DetailView):
    model = UserRoles
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/bd_admin/roles/DetailView.html'
    context_object_name = 'RolesListView'

class RolesUpdateView(UpdateView):
    model = UserRoles
    form_class = UserRolesForm
    pk_url_kwarg = 'pk'
    context_object_name = 'RolesUpdateView'
    template_name = 'bookLibrary/bd_admin/roles/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:RolesListView')

class RolesDeleteView(DeleteView):
    model = UserRoles
    context_object_name = 'RolesDeleteView'
    template_name = 'bookLibrary/bd_admin/roles/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:RolesListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['role'] = get_object_or_404(UserRoles, pk=self.kwargs['pk'])
        return context
    

def my_shelf(request):
    books_with_notes = Books.objects.filter(notes__user=request.user).distinct()
    books_with_bookmarks = Books.objects.filter(bookmarks__user=request.user).distinct()
    books_with_reviews = Books.objects.filter(reviews__user=request.user).distinct()
    
    books = books_with_notes | books_with_bookmarks | books_with_reviews

    books = books.distinct()
    paginator = Paginator(books, 8)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)

    return render(request, 'bookLibrary/my_shelf.html', {'books': books})


@login_required(login_url="login")
def remove_from_shelf(request, book_id):
    book = get_object_or_404(Books, pk=book_id)
    
    Notes.objects.filter(book=book, user=request.user).delete()
    Bookmarks.objects.filter(book=book, user=request.user).delete()
    Reviews.objects.filter(book=book, user=request.user).delete()
    
    messages.success(request, "Книга удалена с вашей полки.")
    return redirect("bookLibrary:my_shelf")


def administrator_page(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'bookLibrary/administrator/administrator_page.html', {'notifications': notifications})


class StudListView(ListView):
    model = Students
    template_name = 'bookLibrary/administrator/students/ListView.html'
    context_object_name = 'StudListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        StudListView = paginator.get_page(page)
        context['StudListView'] = StudListView
        return context


class StudCreateView(CreateView):
    model = Students
    form_class = StudentsForm
    template_name = 'bookLibrary/administrator/students/CreateView.html'
    context_object_name = 'StudCreateView'
    success_url = reverse_lazy('bookLibrary:StudListView')

class StudDetailView(DetailView):
    model = Students
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/students/DetailView.html'
    context_object_name = 'StudListView'

class StudUpdateView(UpdateView):
    model = Students
    form_class = StudentsForm
    pk_url_kwarg = 'pk'
    context_object_name = 'StudUpdateView'
    template_name = 'bookLibrary/administrator/students/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:StudListView')

@csrf_exempt
def import_students(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        try:
            df = pd.read_excel(file, engine='openpyxl')

            for index, row in df.iterrows():
                institution, _ = EducationalInstitution.objects.get_or_create(
                    institution_name=row["Учебное заведение"]
                )

                specialty, _ = Specialties.objects.get_or_create(
                    specialty_name=row["Специальность"],
                    institution=institution
                )

                status = Status.objects.filter(status_name="Не активен").first()
                if not status:
                    return HttpResponse("Ошибка: Статус 'не активен' не найден", status=400)

                Students.objects.create(
                    first_name=row["Имя"],
                    last_name=row["Фамилия"],
                    middle_name=row.get("Отчество", ""),
                    email=row["Электронная почта"],
                    status=status,
                    course=row.get("Курс"),
                    specialty=specialty
                )

            messages.success(request, "Импорт завершен успешно")
        except Exception as e:
            messages.error(request, f"Ошибка при импорте: {str(e)}")

    return redirect("bookLibrary:StudListView")

@login_required
def backup_database(request):
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.sql")

    backup_file = f'"{backup_file}"'

    db_settings = settings.DATABASES['default']

    dump_command = f'$env:PGPASSWORD="{db_settings["PASSWORD"]}"; pg_dump -U {db_settings["USER"]} -h {db_settings["HOST"]} -p {db_settings["PORT"]} -d {db_settings["NAME"]} > {backup_file}'

    try:
        result = subprocess.run(['powershell', '-Command', dump_command], capture_output=True, text=True)

        if result.returncode == 0:
            return HttpResponse(f"Резервная копия создана: {backup_file}")
        else:
            return HttpResponse(f"Ошибка при создании резервной копии: {result.stderr}", status=500)
    except Exception as e:
        return HttpResponse(f"Неизвестная ошибка: {str(e)}", status=500)



class SubjectsListView(ListView):
    model = Subjects
    template_name = 'bookLibrary/administrator/subjects/ListView.html'
    context_object_name = 'SubjectsListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        SubjectsListView = paginator.get_page(page)
        context['SubjectsListView'] = SubjectsListView
        return context


class SubjectsCreateView(CreateView):
    model = Subjects
    form_class = SubjectsForm
    template_name = 'bookLibrary/administrator/subjects/CreateView.html'
    context_object_name = 'SubjectsCreateView'
    success_url = reverse_lazy('bookLibrary:SubjectsListView')

class SubjectsDetailView(DetailView):
    model = Subjects
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/subjects/DetailView.html'
    context_object_name = 'SubjectsListView'

class SubjectsUpdateView(UpdateView):
    model = Subjects
    form_class = SubjectsForm
    pk_url_kwarg = 'pk'
    context_object_name = 'SubjectsUpdateView'
    template_name = 'bookLibrary/administrator/subjects/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:SubjectsListView')

class SubjectsDeleteView(DeleteView):
    model = Subjects
    context_object_name = 'SubjectsDeleteView'
    template_name = 'bookLibrary/administrator/subjects/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:SubjectsListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['subject'] = get_object_or_404(Subjects, pk=self.kwargs['pk'])
        return context
    

class SpecialtiesListView(ListView):
    model = Specialties
    template_name = 'bookLibrary/administrator/specialties/ListView.html'
    context_object_name = 'SpecialtiesListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        SpecialtiesListView = paginator.get_page(page)
        context['SpecialtiesListView'] = SpecialtiesListView
        return context


class SpecialtiesCreateView(CreateView):
    model = Specialties
    form_class = SpecialtiesForm
    template_name = 'bookLibrary/administrator/specialties/CreateView.html'
    context_object_name = 'SpecialtiesCreateView'
    success_url = reverse_lazy('bookLibrary:SpecialtiesListView')

class SpecialtiesDetailView(DetailView):
    model = Specialties
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/specialties/DetailView.html'
    context_object_name = 'SpecialtiesListView'

class SpecialtiesUpdateView(UpdateView):
    model = Specialties
    form_class = SpecialtiesForm
    pk_url_kwarg = 'pk'
    context_object_name = 'SpecialtiesUpdateView'
    template_name = 'bookLibrary/administrator/specialties/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:SpecialtiesListView')

class SpecialtiesDeleteView(DeleteView):
    model = Specialties
    context_object_name = 'SpecialtiesDeleteView'
    template_name = 'bookLibrary/administrator/specialties/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:SpecialtiesListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['specialty'] = get_object_or_404(Specialties, pk=self.kwargs['pk'])
        return context
    

class EducationalInstitutionListView(ListView):
    model = EducationalInstitution
    template_name = 'bookLibrary/administrator/educationalInstitution/ListView.html'
    context_object_name = 'EducationalInstitutionListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        EducationalInstitutionListView = paginator.get_page(page)
        context['EducationalInstitutionListView'] = EducationalInstitutionListView
        return context


class EducationalInstitutionCreateView(CreateView):
    model = EducationalInstitution
    form_class = EducationalInstitutionForm
    template_name = 'bookLibrary/administrator/educationalInstitution/CreateView.html'
    context_object_name = 'EducationalInstitutionCreateView'
    success_url = reverse_lazy('bookLibrary:EducationalInstitutionListView')

class EducationalInstitutionDetailView(DetailView):
    model = EducationalInstitution
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/educationalInstitution/DetailView.html'
    context_object_name = 'EducationalInstitutionListView'

class EducationalInstitutionUpdateView(UpdateView):
    model = EducationalInstitution
    form_class = EducationalInstitutionForm
    pk_url_kwarg = 'pk'
    context_object_name = 'EducationalInstitutionUpdateView'
    template_name = 'bookLibrary/administrator/educationalInstitution/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:EducationalInstitutionListView')

class EducationalInstitutionDeleteView(DeleteView):
    model = EducationalInstitution
    context_object_name = 'EducationalInstitutionDeleteView'
    template_name = 'bookLibrary/administrator/educationalInstitution/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:EducationalInstitutionListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['institution'] = get_object_or_404(EducationalInstitution, pk=self.kwargs['pk'])
        return context


class BooksListView(ListView):
    model = Books
    template_name = 'bookLibrary/administrator/books/ListView.html'
    context_object_name = 'BooksListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        BooksListView = paginator.get_page(page)
        context['BooksListView'] = BooksListView
        return context


class BooksCreateView(CreateView):
    model = Books
    form_class = BooksForm
    template_name = 'bookLibrary/administrator/books/CreateView.html'
    context_object_name = 'BooksCreateView'
    success_url = reverse_lazy('bookLibrary:BooksListView')

class BooksDetailView(DetailView):
    model = Books
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/books/DetailView.html'
    context_object_name = 'BooksListView'

class BooksUpdateView(UpdateView):
    model = Books
    form_class = BooksForm
    pk_url_kwarg = 'pk'
    context_object_name = 'BooksUpdateView'
    template_name = 'bookLibrary/administrator/books/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:BooksListView')

class BooksDeleteView(DeleteView):
    model = Books
    context_object_name = 'BooksDeleteView'
    template_name = 'bookLibrary/administrator/books/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:BooksListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['book'] = get_object_or_404(Books, pk=self.kwargs['pk'])
        return context
    

class GenresListView(ListView):
    model = Genres
    template_name = 'bookLibrary/administrator/genres/ListView.html'
    context_object_name = 'GenresListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        GenresListView = paginator.get_page(page)
        context['GenresListView'] = GenresListView
        return context


class GenresCreateView(CreateView):
    model = Genres
    form_class = GenresForm
    template_name = 'bookLibrary/administrator/genres/CreateView.html'
    context_object_name = 'GenresCreateView'
    success_url = reverse_lazy('bookLibrary:GenresListView')

class GenresDetailView(DetailView):
    model = Genres
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/genres/DetailView.html'
    context_object_name = 'GenresListView'

class GenresUpdateView(UpdateView):
    model = Genres
    form_class = GenresForm
    pk_url_kwarg = 'pk'
    context_object_name = 'GenresUpdateView'
    template_name = 'bookLibrary/administrator/genres/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:GenresListView')

class GenresDeleteView(DeleteView):
    model = Genres
    context_object_name = 'GenresDeleteView'
    template_name = 'bookLibrary/administrator/genres/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:GenresListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['genre'] = get_object_or_404(Genres, pk=self.kwargs['pk'])
        return context
    

class AuthorsListView(ListView):
    model = Authors
    template_name = 'bookLibrary/administrator/authors/ListView.html'
    context_object_name = 'AuthorsListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        AuthorsListView = paginator.get_page(page)
        context['AuthorsListView'] = AuthorsListView
        return context


class AuthorsCreateView(CreateView):
    model = Authors
    form_class = AuthorsForm
    template_name = 'bookLibrary/administrator/authors/CreateView.html'
    context_object_name = 'AuthorsCreateView'
    success_url = reverse_lazy('bookLibrary:AuthorsListView')

class AuthorsDetailView(DetailView):
    model = Authors
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/authors/DetailView.html'
    context_object_name = 'AuthorsListView'

class AuthorsUpdateView(UpdateView):
    model = Authors
    form_class = AuthorsForm
    pk_url_kwarg = 'pk'
    context_object_name = 'AuthorsUpdateView'
    template_name = 'bookLibrary/administrator/authors/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:AuthorsListView')

class AuthorsDeleteView(DeleteView):
    model = Authors
    context_object_name = 'AuthorsDeleteView'
    template_name = 'bookLibrary/administrator/authors/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:AuthorsListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['author'] = get_object_or_404(Authors, pk=self.kwargs['pk'])
        return context
    

class PublishersListView(ListView):
    model = Publishers
    template_name = 'bookLibrary/administrator/publishers/ListView.html'
    context_object_name = 'PublishersListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        PublishersListView = paginator.get_page(page)
        context['PublishersListView'] = PublishersListView
        return context


class PublishersCreateView(CreateView):
    model = Publishers
    form_class = PublishersForm
    template_name = 'bookLibrary/administrator/publishers/CreateView.html'
    context_object_name = 'PublishersCreateView'
    success_url = reverse_lazy('bookLibrary:PublishersListView')

class PublishersDetailView(DetailView):
    model = Publishers
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/publishers/DetailView.html'
    context_object_name = 'PublishersListView'

class PublishersUpdateView(UpdateView):
    model = Publishers
    form_class = PublishersForm
    pk_url_kwarg = 'pk'
    context_object_name = 'PublishersUpdateView'
    template_name = 'bookLibrary/administrator/publishers/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:PublishersListView')

class PublishersDeleteView(DeleteView):
    model = Publishers
    context_object_name = 'PublishersDeleteView'
    template_name = 'bookLibrary/administrator/publishers/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:PublishersListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['publisher'] = get_object_or_404(Publishers, pk=self.kwargs['pk'])
        return context
    
class ReviewsListView(ListView):
    model = Reviews
    template_name = 'bookLibrary/administrator/reviews/ListView.html'
    context_object_name = 'ReviewsListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        ReviewsListView = paginator.get_page(page)
        context['ReviewsListView'] = ReviewsListView
        return context

class ReviewsDetailView(DetailView):
    model = Reviews
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/reviews/DetailView.html'
    context_object_name = 'ReviewsListView'

class ReviewsUpdateView(UpdateView):
    model = Reviews
    form_class = ReviewsForm
    pk_url_kwarg = 'pk'
    context_object_name = 'ReviewsUpdateView'
    template_name = 'bookLibrary/administrator/reviews/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:ReviewsListView')

class ReviewsDeleteView(DeleteView):
    model = Reviews
    context_object_name = 'ReviewsDeleteView'
    template_name = 'bookLibrary/administrator/reviews/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:ReviewsListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['review'] = get_object_or_404(Reviews, pk=self.kwargs['pk'])
        return context
    

class SubjectSpecialtyLinkListView(ListView):
    model = SubjectSpecialtyLink
    template_name = 'bookLibrary/administrator/subjectSpecialtyLink/ListView.html'
    context_object_name = 'SubjectSpecialtyLinkListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        SubjectSpecialtyLinkListView = paginator.get_page(page)
        context['SubjectSpecialtyLinkListView'] = SubjectSpecialtyLinkListView
        return context
    
class SubjectSpecialtyLinkCreateView(CreateView):
    model = SubjectSpecialtyLink
    form_class = SubjectSpecialtyLinkForm
    template_name = 'bookLibrary/administrator/subjectSpecialtyLink/CreateView.html'
    context_object_name = 'SubjectSpecialtyLinkCreateView'
    success_url = reverse_lazy('bookLibrary:SubjectSpecialtyLinkListView')

class SubjectSpecialtyLinkDetailView(DetailView):
    model = SubjectSpecialtyLink
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/subjectSpecialtyLink/DetailView.html'
    context_object_name = 'SubjectSpecialtyLinkListView'

class SubjectSpecialtyLinkUpdateView(UpdateView):
    model = SubjectSpecialtyLink
    form_class = SubjectSpecialtyLinkForm
    pk_url_kwarg = 'pk'
    context_object_name = 'SubjectSpecialtyLinkUpdateView'
    template_name = 'bookLibrary/administrator/subjectSpecialtyLink/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:SubjectSpecialtyLinkListView')

class SubjectSpecialtyLinkDeleteView(DeleteView):
    model = SubjectSpecialtyLink
    context_object_name = 'SubjectSpecialtyLinkDeleteView'
    template_name = 'bookLibrary/administrator/subjectSpecialtyLink/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:SubjectSpecialtyLinkListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['subjectSpecialty'] = get_object_or_404(SubjectSpecialtyLink, pk=self.kwargs['pk'])
        return context
    
class StatusListView(ListView):
    model = Status
    template_name = 'bookLibrary/administrator/status/ListView.html'
    context_object_name = 'StatusListView'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')
        StatusListView = paginator.get_page(page)
        context['StatusListView'] = StatusListView
        return context
    
class StatusCreateView(CreateView):
    model = Status
    form_class = StatusForm
    template_name = 'bookLibrary/administrator/status/CreateView.html'
    context_object_name = 'StatusCreateView'
    success_url = reverse_lazy('bookLibrary:StatusListView')

class StatusDetailView(DetailView):
    model = Status
    pk_url_kwarg = 'pk'
    template_name = 'bookLibrary/administrator/status/DetailView.html'
    context_object_name = 'StatusListView'

class StatusUpdateView(UpdateView):
    model = Status
    form_class = StatusForm
    pk_url_kwarg = 'pk'
    context_object_name = 'StatusUpdateView'
    template_name = 'bookLibrary/administrator/status/UpdateView.html'
    success_url = reverse_lazy('bookLibrary:StatusListView')

class StatusDeleteView(DeleteView):
    model = Status
    context_object_name = 'StatusDeleteView'
    template_name = 'bookLibrary/administrator/status/DeleteView.html'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('bookLibrary:StatusListView')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pk'] = self.kwargs['pk']
        context['status'] = get_object_or_404(Status, pk=self.kwargs['pk'])
        return context
@require_POST
def send_site_update_notification(request):
    print(f"Request method: {request.method}")
    print(f"POST data: {request.POST}")

    title = request.POST.get('title')
    message = request.POST.get('message')
    target_roles = request.POST.getlist('roles')

    if not title or not message or not target_roles:
        messages.error(request, 'Необходимо указать заголовок, сообщение и роли.')
        return redirect('some_admin_page')

    roles = UserRoles.objects.filter(role_name__in=target_roles)
    users = User.objects.filter(role__in=roles)

    for user in users:
        Notification.objects.create(
            user=user,
            title=title,
            message=message
        )

    messages.success(request, 'Уведомление успешно разослано.')
    return redirect('bookLibrary:UsersListView')

@login_required
def send_update_form(request):
    return render(request, 'bookLibrary/bd_admin/notification_page.html')