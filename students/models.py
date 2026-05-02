from django.db import models
from django.conf import settings


class ClassGrade(models.Model):
    """A year/grade level scoped to a school, e.g. 'Grade 7', 'Form 1'."""
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="class_grades"
    )
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ("school", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Section(models.Model):
    """A stream/section within a grade, scoped to a school, e.g. 'East', 'A'."""
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="sections"
    )
    name = models.CharField(max_length=50)
    class_grade = models.ForeignKey(
        "students.ClassGrade",
        on_delete=models.CASCADE,
        related_name="sections"
    )

    class Meta:
        unique_together = ("school", "class_grade", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.class_grade} — {self.name}"


class Classroom(models.Model):
    """Physical/logical classroom linking a grade+section to an optional class teacher."""
    class_grade = models.ForeignKey(
        "students.ClassGrade",
        on_delete=models.CASCADE,
        related_name="classrooms"
    )
    section = models.ForeignKey(
        "students.Section",
        on_delete=models.CASCADE,
        related_name="classrooms"
    )
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classrooms_taught"
    )

    def __str__(self):
        return f"{self.class_grade} - {self.section}"


class Student(models.Model):
    GENDER_CHOICES = [
        ("male",   "Male"),
        ("female", "Female"),
    ]

    BOARDING_CHOICES = [
        ("yes", "Boarder"),
        ("no",  "Day Scholar"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_account"
    )
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="students"
    )
    admission_no = models.CharField(max_length=50, unique=True)

    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    dob        = models.DateField(null=True, blank=True)

    gender  = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    is_boarder = models.CharField(max_length=3, choices=BOARDING_CHOICES, default="no")

    current_class = models.ForeignKey(
        "students.ClassGrade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_students"
    )
    current_section = models.ForeignKey(
        "students.Section",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="current_students"
    )

    parents = models.ManyToManyField(
        "profiles.ParentProfile",
        blank=True,
        related_name="children"
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
