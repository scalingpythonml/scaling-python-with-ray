# -*- coding: utf-8 -*-
import os
import uuid

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.db.models import ExpressionWrapper, Q
from django.utils import timezone

from django_countries.fields import CountryField
from sorl.thumbnail import ImageField, get_thumbnail


__all__ = ("User",)


def _get_user_image_path(instance, filename):
    extension = filename.split(".")[-1].lower()
    hash = uuid.uuid4().hex
    return os.path.join(
        "accounts",
        "users",
        str(instance.pk),
        "depictions",
        "%s.%s" % (hash[:10], extension),
    )


class UserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email, and password.
        Username set default in model uuid.uuid4
        """

        if not email:
            raise ValueError("The given email must be set.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_inactive_user(self, email, password=None, **extra_fields):
        """
        Create and save a inactive user with the given email, and password.
        Username set default in model uuid.uuid4
        """

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", False)
        return self._create_user(email, password, **extra_fields)

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a user with the given email, and password.
        Username set default in model uuid.uuid4
        """

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_active", True)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        """
        Create and save a superuser with the given email, and password.
        Username set default in model uuid.uuid4
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_active") is not True:
            raise ValueError("Superuser must have is_active=True.")

        return self._create_user(email, password, **extra_fields)

    def onboarding_complete_annotate(self, **filters):
        return (
            self.filter(**filters)
            .annotate(
                have_personal_info=ExpressionWrapper(
                    Q(full_name__isnull=False) & Q(country__isnull=False),
                    output_field=models.BooleanField(),
                )
            )
            .annotate(
                user_have_device=ExpressionWrapper(
                    Q(device__isnull=False), output_field=models.BooleanField()
                )
            )
        )

    def update_user_device_nickname(self, user, new_nickname):
        device = user.device
        device.nickname = new_nickname
        device.save()


class User(AbstractBaseUser, PermissionsMixin):
    """
    Inherits from both the AbstractBaseUser and PermissionMixin.
    The following attributes are inherited from the superclasses:
        * password
        * last_login
        * is_superuser

    """

    id = models.BigAutoField(primary_key=True)
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(null=True, blank=True, unique=True)
    thumb = ImageField(upload_to=_get_user_image_path, null=True, blank=True)
    is_staff = models.BooleanField(
        default=False,
        help_text="Designates whether the user can log into this admin site.",
    )
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    company = models.CharField(max_length=100, blank=True, null=True)
    country = CountryField(blank=True, null=True)
    complete_onboarding = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return str(self.id)

    @property
    def device_nickname(self):
        try:
            return self.device.nickname
        except self.device.DoesNotExist:
            return None

    @property
    def have_device(self):
        try:
            return bool(self.device)
        except Exception:
            return False

    @property
    def twillion_number(self):
        return "---"

    @property
    def company_email(self):
        return "---"
