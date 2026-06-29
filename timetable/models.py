from django.db import models
from django.core.exceptions import ValidationError


DAY_CHOICES = [
    ("Monday", "Monday"),
    ("Tuesday", "Tuesday"),
    ("Wednesday", "Wednesday"),
    ("Thursday", "Thursday"),
    ("Friday", "Friday"),
    ("Saturday", "Saturday"),
    ("Sunday", "Sunday"),
]


class Room(models.Model):
    """A physical room or venue in the school."""
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="rooms"
    )
    name = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField(default=30)
    room_type = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g. Classroom, Lab, Hall, Sports Ground"
    )

    class Meta:
        unique_together = ("school", "name")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.school})"
class Period(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="periods",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=50, help_text="e.g. Period 1, Morning Break")
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)

    class Meta:
        ordering = ["start_time"]
        unique_together = ("school", "start_time")

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def __str__(self):
        return f"{self.name} ({self.start_time.strftime('%H:%M')}–{self.end_time.strftime('%H:%M')})"


class TimetableSetting(models.Model):
    classroom = models.OneToOneField(
        "students.Classroom",
        on_delete=models.CASCADE,
        related_name="timetable_setting"
    )
    start_time = models.TimeField(default="08:00")
    end_time = models.TimeField(default="16:00")
    lesson_duration = models.PositiveIntegerField(
        default=45,
        help_text="Lesson duration in minutes"
    )
    days = models.JSONField(
        default=list,
        help_text="Example: ['Monday', 'Tuesday', 'Wednesday']"
    )
    spread_lessons_evenly = models.BooleanField(default=True)
    auto_generate = models.BooleanField(
        default=True,
        help_text="Automatically generate timetable"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.days:
            self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.classroom} Timetable Settings"


class TimetableBreak(models.Model):
    setting = models.ForeignKey(
        TimetableSetting,
        on_delete=models.CASCADE,
        related_name="breaks"
    )
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["start_time"]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("Break end time must be after start time.")

    def __str__(self):
        return f"{self.name}"


class SubjectConfiguration(models.Model):
    setting = models.ForeignKey(
        TimetableSetting,
        on_delete=models.CASCADE,
        related_name="subject_configs"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE
    )
    teacher_assignment = models.ForeignKey(
        "teachers.TeacherSubjectAssignment",
        on_delete=models.CASCADE
    )
    lessons_per_week = models.PositiveIntegerField(default=4)
    fixed_day = models.CharField(
        max_length=20,
        choices=DAY_CHOICES,
        blank=True,
        null=True
    )
    fixed_start_time = models.TimeField(blank=True, null=True)
    is_fixed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("setting", "subject")

    def clean(self):
        if self.is_fixed:
            if not self.fixed_day or not self.fixed_start_time:
                raise ValidationError("Fixed lessons require fixed day and time.")

    def __str__(self):
        return f"{self.subject.name}"


class ClassroomTimetable(models.Model):
    """
    The timetable for a specific classroom in a specific academic year.
    Class teacher pulls entries from MasterTimetableEntry.
    """
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("generated", "Generated"),
        ("conflict", "Conflict"),
        ("published", "Published"),
    ]
    classroom = models.ForeignKey(
        "students.Classroom",
        on_delete=models.CASCADE,
        related_name="classroom_timetables"
    )
    academic_year = models.CharField(max_length=20, default="2025-2026")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )
    created_by = models.ForeignKey(
        "profiles.TeacherProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_timetables"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("classroom", "academic_year")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.classroom} — {self.academic_year} ({self.status})"


class TimetableEntry(models.Model):
    classroom = models.ForeignKey(
        "students.Classroom",
        on_delete=models.CASCADE,
        related_name="timetable_entries"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        "profiles.TeacherProfile",
        on_delete=models.CASCADE
    )
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)
    break_name = models.CharField(max_length=100, blank=True, null=True)
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="timetable_entries"
    )
    timetable = models.ForeignKey(
        ClassroomTimetable,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="legacy_entries"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return f"{self.subject} - {self.day}"


class MasterTimetableEntry(models.Model):
    """
    Admin-created school-wide timetable entry.
    Source of truth — no teacher can appear twice in the same slot.
    """
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="master_timetable_entries"
    )
    teacher = models.ForeignKey(
        "profiles.TeacherProfile",
        on_delete=models.CASCADE,
        related_name="master_entries"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE,
        related_name="master_entries"
    )
    classroom = models.ForeignKey(
        "students.Classroom",
        on_delete=models.CASCADE,
        related_name="master_entries"
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="master_entries"
    )
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    academic_year = models.CharField(
        max_length=20,
        default="2025-2026",
        help_text="e.g. 2025-2026"
    )

    class Meta:
        unique_together = ("teacher", "day", "start_time", "academic_year")
        ordering = ["day", "start_time"]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError("End time must be after start time.")

    def __str__(self):
        return (
            f"{self.teacher} — {self.subject} — "
            f"{self.classroom} — {self.day} {self.start_time}"
        )


class ClassroomTimetableEntry(models.Model):
    """
    A single slot in a classroom timetable.
    Pulled from MasterTimetableEntry — guarantees no teacher conflicts.
    """
    timetable = models.ForeignKey(
        ClassroomTimetable,
        on_delete=models.CASCADE,
        related_name="entries"
    )
    master_entry = models.ForeignKey(
        MasterTimetableEntry,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classroom_entries",
        help_text="The master entry this slot was pulled from"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        "profiles.TeacherProfile",
        on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    day = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)
    break_name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["day", "start_time"]
        unique_together = ("timetable", "day", "start_time")

    def __str__(self):
        return f"{self.subject} — {self.day} {self.start_time}"

class TimetableGenerationConfig(models.Model):
    """School-wide settings for auto-generating the master timetable."""
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="generation_configs"
    )
    academic_year = models.CharField(max_length=20, default="2025-2026")
    lesson_duration = models.PositiveIntegerField(
        default=45,
        help_text="Duration of each lesson in minutes"
    )
    school_start_time = models.TimeField(
        default="08:00",
        help_text="Time the first lesson starts"
    )
    school_end_time = models.TimeField(
        default="15:45",
        help_text="Time the last lesson ends"
    )
    days = models.JSONField(
        default=list,
        help_text="['Monday','Tuesday','Wednesday','Thursday','Friday']"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("school", "academic_year")

    def __str__(self):
        return f"{self.school} — {self.academic_year} config"


class GenerationBreak(models.Model):
    """Breaks defined for auto-generation (separate from TimetableBreak)."""
    config = models.ForeignKey(
        TimetableGenerationConfig,
        on_delete=models.CASCADE,
        related_name="breaks"
    )
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        ordering = ["start_time"]

    def __str__(self):
        return f"{self.name} ({self.start_time}–{self.end_time})"


class ClassroomSubjectConfig(models.Model):
    """
    Defines which subjects are taught in a classroom,
    by which teacher, how many times per week,
    and optional fixed slot.
    """
    SCOPE_CHOICES = [
        ("classroom", "Per Classroom"),
        ("school", "School-wide"),
    ]
    config = models.ForeignKey(
        TimetableGenerationConfig,
        on_delete=models.CASCADE,
        related_name="subject_configs"
    )
    classroom = models.ForeignKey(
        "students.Classroom",
        on_delete=models.CASCADE,
        related_name="subject_configs"
    )
    subject = models.ForeignKey(
        "academics.Subject",
        on_delete=models.CASCADE
    )
    teacher = models.ForeignKey(
        "profiles.TeacherProfile",
        on_delete=models.CASCADE
    )
    lessons_per_week = models.PositiveIntegerField(default=4)
    is_fixed = models.BooleanField(default=False)
    fixed_day = models.CharField(
        max_length=20,
        choices=DAY_CHOICES,
        blank=True,
        null=True
    )
    fixed_start_time = models.TimeField(blank=True, null=True)
    fixed_scope = models.CharField(
        max_length=20,
        choices=SCOPE_CHOICES,
        default="classroom"
    )

    class Meta:
        unique_together = ("config", "classroom", "subject")

    def __str__(self):
        return f"{self.classroom} — {self.subject} ({self.teacher})"


class TimetableGenerationJob(models.Model):
    """Tracks the status of a Celery generation task."""
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("running", "Running"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="generation_jobs"
    )
    academic_year = models.CharField(max_length=20)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    task_id = models.CharField(max_length=255, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    entries_created = models.PositiveIntegerField(default=0)
    conflicts = models.JSONField(default=list)

    def __str__(self):
        return f"{self.school} — {self.academic_year} ({self.status})"