

from django.contrib.auth.models import AbstractUser
from django.db import models
from schools.models import School


class User(AbstractUser):

    ROLE_CHOICES = [
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('payroll', 'Payroll Manager'),
        ('staff', 'Staff'),
        ('bursar', 'Bursar'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    STATUS_CHOICES = [ ("active", "Active"), ("withdrawn", "Withdrawn"), ] 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active") 

    school = models.ForeignKey(
        "schools.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Leave empty for Super Admin"
    )

    phone = models.CharField(max_length=20, blank=True, null=True)

    def is_superadmin(self):
        return self.role == "superadmin"

    def __str__(self):
        return self.username
    must_change_password = models.BooleanField(default=False)

