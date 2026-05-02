from django.db import models
from django.conf import settings
from academics.models import Subject
from profiles.models import TeacherProfile


class Teacher(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_account"
    )
    staff_id = models.CharField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, blank=True)
    assigned_subjects = models.ManyToManyField(
        Subject,
        blank=True,
        related_name="assigned_teachers"
    )

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class TeacherSubjectAssignment(models.Model):
    """
    Links a teacher to a specific subject in a specific classroom.
    A subject teacher can only see/edit results for their own assignments.
    A class teacher can see all assignments within their classroom.
    """
    teacher = models.ForeignKey(
        TeacherProfile,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="teacher_assignments"
    )
    classroom = models.ForeignKey(
        "students.Classroom",
        on_delete=models.CASCADE,
        related_name="subject_assignments"
    )
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="teacher_assignments"
    )

    class Meta:
        unique_together = ("teacher", "subject", "classroom")
        ordering = ["classroom__class_grade__name", "classroom__section__name", "subject__name"]

    def __str__(self):
        return (
            f"{self.teacher.user.get_full_name()} — "
            f"{self.subject.name} — "
            f"{self.classroom}"
        )