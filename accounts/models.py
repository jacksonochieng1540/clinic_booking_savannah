from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Custom User model with additional fields for clinic system
    """

    ROLE_CHOICES = [
        ("patient", "Patient"),
        ("doctor", "Doctor"),
        ("admin", "Admin"),
        ("staff", "Staff"),
    ]

    email = models.EmailField(_("email address"), unique=True)
    phone_number = models.CharField(
        max_length=15,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$")],
        blank=True,
        null=True,
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="patient")

    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pics/", null=True, blank=True)

    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)
    password_reset_token = models.CharField(max_length=255, blank=True, null=True)
    token_created_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_("The groups this user belongs to. A user will get all permissions " "granted to each of their groups."),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ["-date_joined"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    def is_doctor(self):
        return self.role == "doctor"

    def is_patient(self):
        return self.role == "patient"

    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    """
    Extended user profile with additional details
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, null=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True, null=True)
    preferred_language = models.CharField(max_length=10, default="en")
    notifications_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"


class UserActivityLog(models.Model):
    """
    Track user activity for audit purposes
    """

    ACTION_TYPES = [
        ("login", "Login"),
        ("logout", "Logout"),
        ("register", "Register"),
        ("password_reset", "Password Reset"),
        ("profile_update", "Profile Update"),
        ("booking", "Booking Created"),
        ("cancellation", "Booking Cancelled"),
        ("reschedule", "Booking Rescheduled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="activities")
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    details = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "action", "created_at"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.action} - {self.created_at}"
