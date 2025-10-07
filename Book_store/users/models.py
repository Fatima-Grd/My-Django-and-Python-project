from django.db import models
from django.contrib.auth.models import AbstractUser
from users.user_manager import CustomUserManager


class MainUser(AbstractUser):

    username = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        unique=False
    )

    phone_number = models.CharField(max_length=11, unique=True)

    USERNAME_FIELD = "phone_number"

    objects = CustomUserManager()


class Profile(models.Model):
    user = models.OneToOneField(MainUser, on_delete=models.CASCADE)
    national_code = models.CharField(max_length=10, null=True, blank=True)
    address = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.user.phone_number


class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

