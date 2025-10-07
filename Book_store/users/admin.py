from django.contrib import admin
from users.models import MainUser, Profile, Book

admin.site.register(MainUser)
admin.site.register(Profile)
admin.site.register(Book)

