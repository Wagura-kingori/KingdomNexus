from django.db import models
from django.conf import settings


DAYS = [
    ("monday", "Monday"),
    ("tuesday", "Tuesday"),
    ("wednesday", "Wednesday"),
    ("thursday", "Thursday"),
    ("friday", "Friday"),
    ("saturday", "Saturday"),
]


class TimetableSetting(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="timetable_settings"
    )

    classroom = models.ForeignKey(
        "students.Classroom",
        on_delete=models.CASCADE,
        related_name="timetable_settings"
    )

    days = models.JSONField(default=list)   # ["monday","tuesday"...]
    lesson_minutes = models.PositiveIntegerField(default=45)

    start_time = models.TimeField(default="08:00")
    end_time = models.TimeField(default="16:00")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("school", "classroom")

    def __str__(self):
        return f"{self.classroom} timetable settings"


class BreakPeriod(models.Model):
    setting = models.ForeignKey(
        TimetableSetting,
        on_delete=models.CASCADE,
        related_name="breaks"
    )

    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return self.name


class SubjectRule(models.Model):
    setting = models.ForeignKey(
        TimetableSetting,
        on_delete=models.CASCADE,
        related_name="subject_rules"
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE
    )

    weekly_lessons = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.subject.name}"


class FixedLesson(models.Model):
    setting = models.ForeignKey(
        TimetableSetting,
        on_delete=models.CASCADE,
        related_name="fixed_lessons"
    )

    day = models.CharField(max_length=20, choices=DAYS)

    start_time = models.TimeField()

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.subject.name} {self.day}"


class TimetableEntry(models.Model):
    setting = models.ForeignKey(
        TimetableSetting,
        on_delete=models.CASCADE,
        related_name="entries"
    )

    classroom = models.ForeignKey(
        "students.Classroom",
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE
    )

    teacher = models.ForeignKey(
        "profiles.TeacherProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    day = models.CharField(max_length=20, choices=DAYS)

    start_time = models.TimeField()
    end_time = models.TimeField()

    is_fixed = models.BooleanField(default=False)

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return f"{self.classroom} {self.subject.name}"