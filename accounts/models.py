from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from .managers import UserManager

class User(AbstractUser):
    """
    Custom user model that uses email as the unique identifier
    and supports farmer and buyer roles.
    """
    class Role(models.TextChoices):
        FARMER = ('farmer', 'FARMER')
        BUYER = ('buyer', 'BUYER')

    first_name = models.CharField(max_length=120, help_text="User's first name")
    username = models.CharField(max_length=120, blank=True, null=True, help_text="Optional username")
    last_name = models.CharField(max_length=120, help_text="User's last name")
    email = models.EmailField(unique=True, help_text="Email address (used for login)")
    role = models.CharField(
        max_length=10, 
        choices=Role.choices, 
        blank=True, 
        null=True,
        help_text="User role (farmer or buyer)"
    )

    # Add phone number validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{10,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex], 
        max_length=15, 
        blank=True,
        help_text="Contact phone number"
    )

    address = models.TextField(blank=True, help_text="User's address")
    is_active = models.BooleanField(default=True, help_text="Designates whether this user is active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    EMAIL_FIELD = 'email'

    class Meta:
        db_table = 'store_customer'
        indexes = [
            models.Index(fields=['first_name', 'last_name'])
        ]

        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    @property
    def is_farmer(self):
        """Check if user is a farmer"""
        return self.role == self.Role.FARMER

    @property
    def is_buyer(self):
        """Check if user is a buyer"""
        return self.role == self.Role.BUYER
