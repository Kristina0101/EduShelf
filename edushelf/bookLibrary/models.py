from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from .encryption import encrypt_email, decrypt_email

# Create your models here.

class EducationalInstitution(models.Model):
    institution_id = models.AutoField(primary_key=True)
    institution_name = models.CharField(max_length=255)
    contract_date = models.DateField(null=True, blank=True)
    contract_duration = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.institution_name

    class Meta:
        db_table = 'educational_institution'

class Specialties(models.Model):
    specialty_id = models.AutoField(primary_key=True)
    specialty_name = models.CharField(max_length=255)
    institution = models.ForeignKey(EducationalInstitution, on_delete=models.CASCADE)

    def __str__(self):
        return self.specialty_name

    class Meta:
        db_table = 'specialties'

class Status(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.CharField(max_length=255)

    def __str__(self):
        return self.status_name
    class Meta:
        db_table = 'status'

class Subjects(models.Model):
    subject_id = models.AutoField(primary_key=True)
    subject_name = models.CharField(max_length=255)

    def __str__(self):
        return self.subject_name
    class Meta:
        db_table = 'subjects'

class SubjectSpecialtyLink(models.Model):
    subject_specialty_id = models.AutoField(primary_key=True)
    specialty = models.ForeignKey(Specialties, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    course = models.IntegerField()

    def __str__(self):
        return f"{self.subject.subject_name} — {self.specialty.specialty_name} (Курс {self.course})"

    class Meta:
        db_table = 'subject_specialty_link'

class UserRoles(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.role_name
    
    class Meta:
        db_table = 'user_roles'

class User(AbstractUser):
    email = models.CharField(max_length=255, unique=True, null=True, blank=True)
    encrypted_email = models.CharField(max_length=255, blank=True, null=True)
    role = models.ForeignKey('UserRoles', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.email:
            self.encrypted_email = encrypt_email(self.email)  # Шифруем email перед сохранением
        super().save(*args, **kwargs)

    def get_decrypted_email(self):
        return decrypt_email(self.encrypted_email) if self.encrypted_email else None

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'auth_user'

class Students(models.Model):
    student_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, unique=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE)
    course = models.IntegerField(null=True, blank=True)
    specialty = models.ForeignKey(Specialties, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, db_column='users_id')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    class Meta:
        db_table = 'students'

class Genres(models.Model):
    genre_id = models.AutoField(primary_key=True)
    genre_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.genre_name
    
    class Meta:
        db_table = 'genres'

class Authors(models.Model):
    author_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    class Meta:
        db_table = 'authors'

class Publishers(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    publisher_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.publisher_name
    class Meta:
        db_table = 'publishers'

class Books(models.Model):
    book_id = models.AutoField(primary_key=True)
    book_title = models.CharField(max_length=255)
    author = models.ForeignKey(Authors, on_delete=models.CASCADE)
    photo_book = models.ImageField(upload_to='book/%Y/%m/%d')
    book_file = models.FileField(upload_to='file_books/%Y/%m/%d')
    publication_year = models.IntegerField(null=True, blank=True)
    page_count = models.IntegerField(null=True, blank=True)
    genre = models.ForeignKey(Genres, on_delete=models.CASCADE)
    publisher = models.ForeignKey(Publishers, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)

    def __str__(self):
        return self.book_title
    class Meta:
        db_table = 'books'

class Notes(models.Model):
    note_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='users_id')
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    page_number = models.IntegerField()
    note_content = models.TextField(verbose_name="Заметка")
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Заметка на странице {self.page_number} от {self.user.username}'
    
    class Meta:
        db_table = 'notes'

class Bookmarks(models.Model):
    bookmark_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='users_id')
    book = models.ForeignKey(Books, on_delete=models.CASCADE)
    page_number = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Закладка: {self.user.username} — {self.book.book_title} (стр. {self.page_number})"
    
    class Meta:
        db_table = 'bookmarks'

class Reviews(models.Model):
    review_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='users_id', verbose_name="Пользователь")
    book = models.ForeignKey(Books, on_delete=models.CASCADE, verbose_name="Книга")
    rating = models.IntegerField(verbose_name="Рейтинг")
    review_text = models.TextField(verbose_name="Текст отзыва")
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Отзыв от {self.user.username} о книге {self.book.book_title}"

    class Meta:
        db_table = 'reviews'
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']