from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string

from .models import (
    TeacherProfile,
    
    ParentProfile,
    PayrollProfile,
)

User = get_user_model()
def generate_employee_number():
    return get_random_string(8).upper()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create role-based profiles safely.
    Ensures required fields like school are present.
    Prevents duplicates.
    """

    if not created:
        return

   
    school = getattr(instance, "school", None)

    if instance.role == "teacher":
        if school:
            TeacherProfile.objects.get_or_create(
                user=instance,
                
                defaults={"school": school,
                          "employee_number":generate_employee_number(),}
            )

    elif instance.role == "student":
        pass

    elif instance.role == "parent":
        ParentProfile.objects.get_or_create(user=instance)

    elif instance.role == "payroll":
        if school:
            PayrollProfile.objects.get_or_create(
                user=instance,
                defaults={"school": school}
            )