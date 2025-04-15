from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from bookLibrary.models import (
    Authors, 
    Genres, 
    Publishers, 
    Subjects, 
    Books, 
    Bookmarks
)
from bookLibrary.views import add_bookmark
import json

User = get_user_model()

class AddBookmarkTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Создаем необходимые связанные объекты
        self.author = Authors.objects.create(
            first_name='Test',
            last_name='Author'
        )
        self.genre = Genres.objects.create(
            genre_name='Test Genre'
        )
        self.publisher = Publishers.objects.create(
            publisher_name='Test Publisher'
        )
        self.subject = Subjects.objects.create(
            subject_name='Test Subject'
        )
        
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        # Создаем тестовую книгу с временными файлами
        self.book = Books.objects.create(
            book_title='Test Book',
            author=self.author,
            genre=self.genre,
            publisher=self.publisher,
            subject=self.subject,
            photo_book=SimpleUploadedFile("test.jpg", b"file_content"),
            book_file=SimpleUploadedFile("test.pdf", b"file_content"),
            publication_year=2023,
            page_count=300
        )
        
        self.url = f'/books/{self.book.id}/bookmark/'
    
    def tearDown(self):
        # Очищаем созданные объекты после каждого теста
        Bookmarks.objects.all().delete()
        Books.objects.all().delete()
        User.objects.all().delete()
        Authors.objects.all().delete()
        Genres.objects.all().delete()
        Publishers.objects.all().delete()
        Subjects.objects.all().delete()

    def test_add_bookmark_success(self):
        """Test successfully adding a new bookmark"""
        data = {'page_number': 42}
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user = self.user
        
        response = add_bookmark(request, self.book.id)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['message'], 'Закладка успешно добавлена')
        self.assertEqual(Bookmarks.objects.count(), 1)
        
    def test_add_duplicate_bookmark(self):
        """Test adding a duplicate bookmark"""
        # Сначала создаем закладку
        Bookmarks.objects.create(
            book=self.book,
            user=self.user,
            page_number=42
        )
        
        data = {'page_number': 42}
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user = self.user
        
        response = add_bookmark(request, self.book.id)
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], 'Закладка на этой странице уже существует')
        self.assertEqual(Bookmarks.objects.count(), 1)
        
    def test_add_bookmark_unauthenticated(self):
        """Test that unauthenticated users get redirected"""
        data = {'page_number': 42}
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        # Не устанавливаем request.user
        
        response = add_bookmark(request, self.book.id)
        
        self.assertEqual(response.status_code, 302)  # Должен быть редирект на логин
        
    def test_add_bookmark_invalid_book(self):
        """Test with non-existent book ID"""
        invalid_book_id = 9999
        data = {'page_number': 42}
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user = self.user
        
        response = add_bookmark(request, invalid_book_id)
        self.assertEqual(response.status_code, 404)
        
    def test_add_bookmark_missing_page_number(self):
        """Test with missing page_number in request data"""
        data = {}  # Нет page_number
        request = self.factory.post(
            self.url,
            data=json.dumps(data),
            content_type='application/json'
        )
        request.user = self.user
        
        response = add_bookmark(request, self.book.id)
        self.assertEqual(response.status_code, 400)
        
    def test_add_bookmark_invalid_method(self):
        """Test with GET request instead of POST"""
        request = self.factory.get(self.url)
        request.user = self.user
        
        response = add_bookmark(request, self.book.id)
        self.assertEqual(response.status_code, 405)  # Method Not Allowed
