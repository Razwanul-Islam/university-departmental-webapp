from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, password2=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        user = self.model(
            email=self.normalize_email(email).lower(), name=name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.update(is_admin=True, user_type="H", is_active=True)
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email", max_length=250, unique=True)
    USER_CHOICES = [("H", "Head"), ("T", "Teacher"), ("S", "Student")]
    user_type = models.CharField(max_length=9, choices=USER_CHOICES, default="S")
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin
