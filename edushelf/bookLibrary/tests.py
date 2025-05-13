from django.test import TestCase, RequestFactory
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.http import Http404

from .models import *
from .views import StudentsUpdateView, StudentsCreateView
from .forms import StudentsForm

class StudentsViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.institution = EducationalInstitution.objects.create(
            institution_name='Test University'
        )
        
        cls.status = Status.objects.create(
            status_name='Active'
        )
        
        cls.specialty = Specialties.objects.create(
            specialty_name='Computer Science',
            institution=cls.institution
        )
        
        cls.user = User.objects.create_user(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        
        cls.student = Students.objects.create(
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            status=cls.status,
            specialty=cls.specialty,
            user=cls.user
        )
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def _add_messages_to_request(self, request):
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        return request
    
    def test_student_create_view_get(self):
        url = reverse('bookLibrary:StudentsCreateView')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookLibrary/bd_admin/students/CreateView.html')
        self.assertIsInstance(response.context['form'], StudentsForm)
    
    def test_student_create_valid_data(self):
        url = reverse('bookLibrary:StudentsCreateView')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'status': self.status.status_id,
            'specialty': self.specialty.specialty_id,
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('bookLibrary:StudentsListView'))
        self.assertTrue(Students.objects.filter(email='jane.smith@example.com').exists())
    
    def test_student_create_invalid_email(self):
        url = reverse('bookLibrary:StudentsCreateView')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'invalid-email',
            'status': self.status.status_id,
            'specialty': self.specialty.specialty_id,
        }
        response = self.client.post(url, data)
        
        if response.status_code == 200:
            form = response.context['form']
            self.assertFalse(form.is_valid())
            self.assertIn('email', form.errors)
        else:
            self.assertEqual(response.status_code, 302)
            self.assertFalse(Students.objects.filter(email='invalid-email').exists())
            self.assertRedirects(response, reverse('bookLibrary:StudentsListView'))
    
    def test_student_create_duplicate_email(self):
        url = reverse('bookLibrary:StudentsCreateView')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'john.doe@example.com',
            'status': self.status.status_id,
            'specialty': self.specialty.specialty_id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('email', form.errors)
    
    def test_student_create_form_invalid(self):
        request = self.factory.post(reverse('bookLibrary:StudentsCreateView'), {})
        request = self._add_messages_to_request(request)
        request.user = self.user
        
        view = StudentsCreateView()
        view.setup(request)
        view.object = None
        response = view.form_invalid(view.get_form())
        self.assertEqual(response.status_code, 200)
    
    def test_student_create_exception_handling(self):
        request = self.factory.post(reverse('bookLibrary:StudentsCreateView'), {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@example.com',
            'status': self.status.status_id,
            'specialty': self.specialty.specialty_id,
        })
        request = self._add_messages_to_request(request)
        request.user = self.user
        
        view = StudentsCreateView()
        view.setup(request)
        view.object = None
        
        form = view.get_form()
        form.save = lambda: 1/0
        
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 200)
    
    def test_student_update_view_get(self):
        url = reverse('bookLibrary:StudentsUpdateView', kwargs={'pk': self.student.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookLibrary/bd_admin/students/UpdateView.html')
        self.assertEqual(response.context['StudentsUpdateView'], self.student)
    
    def test_student_update_valid_data(self):
        url = reverse('bookLibrary:StudentsUpdateView', kwargs={'pk': self.student.pk})
        data = {
            'first_name': 'John',
            'last_name': 'Doe Updated',
            'email': 'john.doe@example.com',
            'status': self.status.status_id,
            'specialty': self.specialty.specialty_id,
        }
        response = self.client.post(url, data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('bookLibrary:StudentsListView'))
        self.student.refresh_from_db()
        self.assertEqual(self.student.last_name, 'Doe Updated')
    
    def test_student_update_invalid_data(self):
        url = reverse('bookLibrary:StudentsUpdateView', kwargs={'pk': self.student.pk})
        data = {
            'first_name': '',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'status': self.status.status_id,
            'specialty': self.specialty.specialty_id,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertIn('first_name', form.errors)
    
    def test_student_update_form_invalid(self):
        request = self.factory.post(reverse('bookLibrary:StudentsUpdateView', kwargs={'pk': self.student.pk}), {})
        request = self._add_messages_to_request(request)
        request.user = self.user
        
        view = StudentsUpdateView()
        view.setup(request, pk=self.student.pk)
        view.object = self.student
        response = view.form_invalid(view.get_form())
        self.assertEqual(response.status_code, 200)
    
    def test_student_update_exception_handling(self):
        request = self.factory.post(reverse('bookLibrary:StudentsUpdateView', kwargs={'pk': self.student.pk}), {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@example.com',
            'status': self.status.status_id,
            'specialty': self.specialty.specialty_id,
        })
        request = self._add_messages_to_request(request)
        request.user = self.user
        
        view = StudentsUpdateView()
        view.setup(request, pk=self.student.pk)
        view.object = self.student
        
        form = view.get_form()
        form.save = lambda: 1/0
        
        response = view.form_valid(form)
        self.assertEqual(response.status_code, 200)
    
    def test_student_update_nonexistent_pk(self):
        url = reverse('bookLibrary:StudentsUpdateView', kwargs={'pk': 9999})
        try:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 404)
        except Http404:
            pass 