from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("School Assignment", {
            "fields": ("role", "school", "phone")
        }),
    )

    list_display = ("username", "role", "school", "is_staff")
    list_filter = ("role", "school")

    def save_model(self, request, obj, form, change):
        # Super admin must not have a school
        if obj.role == "superadmin":
            obj.school = None
        super().save_model(request, obj, form, change)
