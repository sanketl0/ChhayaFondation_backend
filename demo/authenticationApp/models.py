from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    mobile_number = models.CharField(blank=True, null=True)
    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name="groups",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        related_name="custom_user_set",  # Added related_name
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_user_set",  # Added related_name
        related_query_name="user",
    )

    class Meta:
        permissions = (("can_view_customuser", "Can view custom user"),)

    def __str__(self):
        return self.username
        # return f'{self.first_name} {self.last_name}'


class PendingUser(models.Model):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Store hashed password
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username