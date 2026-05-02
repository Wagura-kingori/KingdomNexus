from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="teacher_profile"
    )
    employee_number = models.CharField(max_length=50, unique=True)
    department = models.CharField(max_length=100, blank=True)
    is_class_teacher = models.BooleanField(default=False)

    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="teachers"
    )

    subjects = models.ManyToManyField(
        "academics.Subject",
        blank=True,
        related_name="teacher_profiles"
    )

    def __str__(self):
        return f"Teacher: {self.user.get_full_name()}"


class StudentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="student_profile"
    )
    admission_number = models.CharField(max_length=50, unique=True)
    classroom = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Student: {self.user.get_full_name()}"


class ParentProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="parent_profile"
    )
    occupation = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"Parent: {self.user.get_full_name()}"


class PayrollProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="payroll_profile"
    )
    staff_number = models.CharField(max_length=50, unique=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bank_name = models.CharField(max_length=100)
    bank_account = models.CharField(max_length=50)

    def __str__(self):
        return f"Payroll: {self.user.get_full_name()}"
