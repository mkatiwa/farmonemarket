from django.contrib.auth.models import AbstractUser
from django.contrib.staticfiles.views import serve
from django.db import models
from .managers import UserManager

# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        FARMER =('farmer', 'FARMER')
        BUYER =('buyer', 'BUYER')

    first_name = models.CharField(max_length=120)
    username = models.CharField(max_length=120, blank=True, null=True)
    last_name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role']
    EMAIL_FIELD = 'email'
    def __str__(self):
        return self.first_name

    @property
    def is_farmer(self):
        return self.role == 'farmer'

    @property
    def is_customer(self):
        return self.role == 'customer'
