from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from .import views
from .views import *

app_name = 'bookLibrary'
urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('bd_admin/', views.bd_admin_page, name='bd_admin_page'),
    path('administrator/', views.administrator_page, name='administrator_page'),
    path('catalog/', views.catalog, name='catalog'),
    path('my_shelf/', views.my_shelf, name='my_shelf'),
    path('catalog/description_book/<int:id>/', views.description_book, name='description_book'),
    path('note/delete/<int:note_id>/', views.delete_note, name='delete_note'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),
    path('book/<int:book_id>/add_bookmark/', views.add_bookmark, name='add_bookmark'),
    path('delete_bookmark/<int:bookmark_id>/', views.delete_bookmark, name='delete_bookmark'),

    path('logs/', log_view, name='log_view'),

    path('bd_admin/students/', views.StudentsListView.as_view(), name='StudentsListView'),
    path('bd_admin/students/create/', views.StudentsCreateView.as_view(), name='StudentsCreateView'),
    path('bd_admin/students/detail/<int:pk>/', views.StudentsDetailView.as_view(), name='StudentsDetailView'),
    path('bd_admin/students/<int:pk>/update/', views.StudentsUpdateView.as_view(), name='StudentsUpdateView'),
    path('bd_admin/students/<int:pk>/delete/', views.StudentsDeleteView.as_view(), name='Students_delete'),

    path('bd_admin/users/', views.UsersListView.as_view(), name='UsersListView'),
    path('bd_admin/users/create/', views.UsersCreateView.as_view(), name='UsersCreateView'),
    path('bd_admin/users/detail/<int:pk>/', views.UsersDetailView.as_view(), name='UsersDetailView'),
    path('bd_admin/users/<int:pk>/update/', views.UsersUpdateView.as_view(), name='UsersUpdateView'),
    path('bd_admin/users/<int:pk>/delete/', views.UsersDeleteView.as_view(), name='Users_Delete'),

    path('bd_admin/roles/', views.RolesListView.as_view(), name='RolesListView'),
    path('bd_admin/roles/create/', views.RolesCreateView.as_view(), name='RolesCreateView'),
    path('bd_admin/roles/detail/<int:pk>/', views.RolesDetailView.as_view(), name='RolesDetailView'),
    path('bd_admin/roles/<int:pk>/update/', views.RolesUpdateView.as_view(), name='RolesUpdateView'),
    path('bd_admin/roles/<int:pk>/delete/', views.RolesDeleteView.as_view(), name='Roles_Delete'),
    path('backup/', backup_database, name='backup_database'),

    path('administrator/students/', views.StudListView.as_view(), name='StudListView'),
    path('administrator/students/create/', views.StudCreateView.as_view(), name='StudCreateView'),
    path('administrator/students/detail/<int:pk>/', views.StudDetailView.as_view(), name='StudDetailView'),
    path('administrator/students/<int:pk>/update/', views.StudUpdateView.as_view(), name='StudUpdateView'),

    path('import_students/', import_students, name='import_students'),
    
    path('administrator/subjects/', views.SubjectsListView.as_view(), name='SubjectsListView'),
    path('administrator/subjects/create/', views.SubjectsCreateView.as_view(), name='SubjectsCreateView'),
    path('administrator/subjects/detail/<int:pk>/', views.SubjectsDetailView.as_view(), name='SubjectsDetailView'),
    path('administrator/subjects/<int:pk>/update/', views.SubjectsUpdateView.as_view(), name='SubjectsUpdateView'),
    path('administrator/subjects/<int:pk>/delete/', views.SubjectsDeleteView.as_view(), name='Subjects_Delete'),

    path('administrator/specialties/', views.SpecialtiesListView.as_view(), name='SpecialtiesListView'),
    path('administrator/specialties/create/', views.SpecialtiesCreateView.as_view(), name='SpecialtiesCreateView'),
    path('administrator/specialties/detail/<int:pk>/', views.SpecialtiesDetailView.as_view(), name='SpecialtiesDetailView'),
    path('administrator/specialties/<int:pk>/update/', views.SpecialtiesUpdateView.as_view(), name='SpecialtiesUpdateView'),
    path('administrator/specialties/<int:pk>/delete/', views.SpecialtiesDeleteView.as_view(), name='Specialties_Delete'),
    
    path('administrator/institutions/', views.EducationalInstitutionListView.as_view(), name='EducationalInstitutionListView'),
    path('administrator/institutions/create/', views.EducationalInstitutionCreateView.as_view(), name='EducationalInstitutionCreateView'),
    path('administrator/institutions/detail/<int:pk>/', views.EducationalInstitutionDetailView.as_view(), name='EducationalInstitutionDetailView'),
    path('administrator/institutions/<int:pk>/update/', views.EducationalInstitutionUpdateView.as_view(), name='EducationalInstitutionUpdateView'),
    path('administrator/institutions/<int:pk>/delete/', views.EducationalInstitutionDeleteView.as_view(), name='Institution_Delete'),

    path('administrator/books/', views.BooksListView.as_view(), name='BooksListView'),
    path('administrator/books/create/', views.BooksCreateView.as_view(), name='BooksCreateView'),
    path('administrator/books/detail/<int:pk>/', views.BooksDetailView.as_view(), name='BooksDetailView'),
    path('administrator/books/<int:pk>/update/', views.BooksUpdateView.as_view(), name='BooksUpdateView'),
    path('administrator/books/<int:pk>/delete/', views.BooksDeleteView.as_view(), name='Books_Delete'),

    path('administrator/genres/', views.GenresListView.as_view(), name='GenresListView'),
    path('administrator/genres/create/', views.GenresCreateView.as_view(), name='GenresCreateView'),
    path('administrator/genres/detail/<int:pk>/', views.GenresDetailView.as_view(), name='GenresDetailView'),
    path('administrator/genres/<int:pk>/update/', views.GenresUpdateView.as_view(), name='GenresUpdateView'),
    path('administrator/genres/<int:pk>/delete/', views.GenresDeleteView.as_view(), name='Genres_Delete'),

    path('administrator/authors/', views.AuthorsListView.as_view(), name='AuthorsListView'),
    path('administrator/authors/create/', views.AuthorsCreateView.as_view(), name='AuthorsCreateView'),
    path('administrator/authors/detail/<int:pk>/', views.AuthorsDetailView.as_view(), name='AuthorsDetailView'),
    path('administrator/authors/<int:pk>/update/', views.AuthorsUpdateView.as_view(), name='AuthorsUpdateView'),
    path('administrator/authors/<int:pk>/delete/', views.AuthorsDeleteView.as_view(), name='Authors_Delete'),

    path('administrator/publishers/', views.PublishersListView.as_view(), name='PublishersListView'),
    path('administrator/publishers/create/', views.PublishersCreateView.as_view(), name='PublishersCreateView'),
    path('administrator/publishers/detail/<int:pk>/', views.PublishersDetailView.as_view(), name='PublishersDetailView'),
    path('administrator/publishers/<int:pk>/update/', views.PublishersUpdateView.as_view(), name='PublishersUpdateView'),
    path('administrator/publishers/<int:pk>/delete/', views.PublishersDeleteView.as_view(), name='Publishers_Delete'),

    path('administrator/reviews/', views.ReviewsListView.as_view(), name='ReviewsListView'),
    path('administrator/reviews/detail/<int:pk>/', views.ReviewsDetailView.as_view(), name='ReviewsDetailView'),
    path('administrator/reviews/<int:pk>/update/', views.ReviewsUpdateView.as_view(), name='ReviewsUpdateView'),
    path('administrator/reviews/<int:pk>/delete/', views.ReviewsDeleteView.as_view(), name='Reviews_Delete'),

    path('administrator/subjectSpecialtyLink/', views.SubjectSpecialtyLinkListView.as_view(), name='SubjectSpecialtyLinkListView'),
    path('administrator/subjectSpecialtyLink/create/', views.SubjectSpecialtyLinkCreateView.as_view(), name='SubjectSpecialtyLinkCreateView'),
    path('administrator/subjectSpecialtyLink/detail/<int:pk>/', views.SubjectSpecialtyLinkDetailView.as_view(), name='SubjectSpecialtyLinkDetailView'),
    path('administrator/subjectSpecialtyLink/<int:pk>/update/', views.SubjectSpecialtyLinkUpdateView.as_view(), name='SubjectSpecialtyLinkUpdateView'),
    path('administrator/subjectSpecialtyLink/<int:pk>/delete/', views.SubjectSpecialtyLinkDeleteView.as_view(), name='SubjectSpecialty_Delete'),

    path('administrator/status/', views.StatusListView.as_view(), name='StatusListView'),
    path('administrator/status/create/', views.StatusCreateView.as_view(), name='StatusCreateView'),
    path('administrator/status/detail/<int:pk>/', views.StatusDetailView.as_view(), name='StatusDetailView'),
    path('administrator/status/<int:pk>/update/', views.StatusUpdateView.as_view(), name='StatusUpdateView'),
    path('administrator/status/<int:pk>/delete/', views.StatusDeleteView.as_view(), name='Status_Delete'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)