from rest_framework import serializers

from django.db import models
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.utils.translation import gettext_lazy as _


# crate custom user and superuser
class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


# custom User class methods for creating and updating users from models
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=35, unique=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    USERNAME_FIELD = "email"

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    objects = UserManager()

    def __str__(self):
        return self.email

    @staticmethod
    def password_validater(password, password1):
        if password != password1:
            raise serializers.ValidationError(
                {"detail": "passwords doesnt match"}
            )
        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {"passwords errors": list(e.messages)}
            )

    @staticmethod
    def check_pass(password, object):
        if not object.check_password(password):
            return False

    @staticmethod
    def set_pass(password, object):
        object.set_password(password)
        object.save()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=35)
    last_name = models.CharField(max_length=35)
    description = models.TextField()

    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email
