from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Q

class UserManager(BaseUserManager):
    def create_user(self, name, phone_number=None, email=None, password=None, **extra_fields):
        """
        Creates and saves a User with the given name, phone_number or email, and password.
        Either phone_number or email must be provided.
        """
        if not name:
            raise ValueError("The Name field is required")
        if not phone_number and not email:
            raise ValueError("Either a phone number or email must be provided")

        email = self.normalize_email(email) if email else None
        user = self.model(
            name=name,
            phone_number=phone_number,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, phone_number=None, email=None, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given name, phone_number or email, and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(name, phone_number, email, password, **extra_fields)

    def get_by_identifier(self, identifier):
        """
        Retrieves a user by phone_number or email.
        """
        return self.get(Q(phone_number=identifier) | Q(email=identifier))

