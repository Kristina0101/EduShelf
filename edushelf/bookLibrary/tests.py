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
