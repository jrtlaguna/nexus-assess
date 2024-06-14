from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import OPTIONAL


def get_admin_group():
    try:
        return Group.objects.get(name="Admins")
    except Group.DoesNotExist:
        return None


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Users require an email field")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    class UserType(models.TextChoices):
        CLIENT = "client", _("Client")
        ADMINISTRATOR = "administrator", _("Administrator")

    username = None
    company = models.ForeignKey(
        "users.Company",
        verbose_name=_("Company"),
        related_name="users",
        on_delete=models.CASCADE,
        **OPTIONAL,
    )
    user_type = models.CharField(
        verbose_name=_("User Type"),
        max_length=50,
        choices=UserType.choices,
        default=UserType.CLIENT,
    )
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.get_display_name(with_company=True)

    def get_display_name(self, with_company=False):
        names = []

        if with_company and self.user_type == self.UserType.ADMINISTRATOR:
            names.append(f"[Nexus Admin]")
        elif with_company and self.company:
            names.append(f"[{self.company}]")

        if self.first_name:
            names.append(self.first_name)
        if self.last_name:
            names.append(self.last_name)

        if not self.first_name and not self.last_name:
            names.append(self.email)

        return " ".join(names)

    def clean(self):
        super().clean()

        if self.user_type != self.UserType.ADMINISTRATOR and self.is_superuser:
            raise ValidationError(
                {"user_type": ["Non-admin users cannot be Superusers."]}
            )

        try:
            self.first_name = self.first_name.encode("ascii", "strict").decode("utf-8")
        except UnicodeEncodeError:
            raise ValidationError(
                {"first_name": ["Non-ascii characters not allowed in first name."]}
            )

        try:
            self.last_name = self.last_name.encode("ascii", "strict").decode("utf-8")
        except UnicodeEncodeError:
            raise ValidationError(
                {"last_name": ["Non-ascii characters not allowed in last name."]}
            )

    def save(self, *args, **kwargs):
        admin_group = get_admin_group()

        if self.is_superuser:
            self.user_type = self.UserType.ADMINISTRATOR
            self.is_staff = True
        else:
            if self.user_type == self.UserType.ADMINISTRATOR:
                self.is_staff = True
                if admin_group:
                    admin_group.user_set.add(self)
            else:
                if admin_group:
                    admin_group.user_set.remove(self)
                self.is_staff = False

        super().save(*args, **kwargs)


class Company(models.Model):
    name = models.CharField(max_length=256, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")
