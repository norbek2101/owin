from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255)
    phone_number = PhoneNumberField(blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'  # Used for authentication; can be None if using custom backend
    REQUIRED_FIELDS = ['name']  # Name is required during creation

    def __str__(self):
        return self.name