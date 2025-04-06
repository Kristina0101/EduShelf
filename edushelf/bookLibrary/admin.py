from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
admin.site.register(EducationalInstitution)
admin.site.register(Specialties)
admin.site.register(Subjects)
admin.site.register(SubjectSpecialtyLink)
admin.site.register(UserRoles)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'encrypted_email', 'role')
    fieldsets = UserAdmin.fieldsets + ((None, {'fields': ('role',)}),)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Students)
admin.site.register(Genres)
admin.site.register(Authors)
admin.site.register(Publishers)
admin.site.register(Books)
admin.site.register(Notes)
admin.site.register(Bookmarks)
admin.site.register(Reviews)
admin.site.register(Status)