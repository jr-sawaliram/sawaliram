"""Define all data models for creating and managing users"""

from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin)
from django.db import models


class UserManager(BaseUserManager):
    """Define the manager to handle user creation"""

    def create_user(self, first_name, last_name, email, password):
        """
        Creates and saves a User with email and organisation
        """
        if not email:
            raise ValueError("Email must be provided to create a user")
        email = self.normalize_email(email)
        user = self.model(email=email)
        user.set_password(password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a user as superuser
        """
        email = self.normalize_email(email)
        user = self.create_user(email, password)
        user.is_staff()
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Define the data model for user"""

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    organisation = models.CharField(max_length=200, default='')

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def get_short_name(self):
        """
        Return the first_name of the user
        """
        return self.first_name

    def get_full_name(self):
        """
        Return the full name of the user
        """
        return self.first_name + ' ' + self.last_name

    def is_staff(self):
        """
        Return whether the user is allowed access to the admin interface
        """
        return self.is_superuser


class VolunteerRequest(models.Model):
    """Define the data model for a volunteer request by a user"""

    class Meta:
        db_table = 'volunteer_request'

    user = models.ForeignKey(
        'sawaliram_auth.User',
        related_name='volunteer_requests',
        on_delete=models.PROTECT)
    expert = models.BooleanField(default=False)
    writer = models.BooleanField(default=False)
    translator = models.BooleanField(default=False)
    expert_application = models.TextField(null=True)
    writer_application = models.TextField(null=True)
    translator_application = models.TextField(null=True)
