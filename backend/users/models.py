from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    email = models.EmailField(
        unique=True,
        verbose_name='email address')
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='user name')
    first_name = models.CharField(
        max_length=150,
        verbose_name='first name')
    last_name = models.CharField(
        max_length=150,
        verbose_name='last name')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    objects = CustomUserManager()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.username
