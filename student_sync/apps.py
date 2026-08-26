from django.apps import AppConfig


class StudentSyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "student_sync"
    verbose_name = "Student Event Sync (fees-service)"

    def ready(self):
        from django.db.models.signals import m2m_changed
        from . import signals  # noqa: F401  (registers the post_save @receiver)

        # Wired here rather than in signals.py — the real Student model
        # (and its parents.through table) isn't available at import time,
        # only once the app registry is fully loaded.
        from students.models import Student
        m2m_changed.connect(
            signals.on_student_parents_changed,
            sender=Student.parents.through,
        )
