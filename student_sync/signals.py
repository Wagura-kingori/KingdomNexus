"""
Connects Django model signals to the event publisher.

Built against the real students.Student model (admission_no, first_name,
last_name, current_class -> ClassGrade.name, parents M2M -> ParentProfile,
no status field). See publisher.py for the wire shape this maps into.

Known gaps, both flagged rather than silently guessed:
  - No status field on Student, so there's nothing to watch for a
    withdrawal via post_save. Call publisher.student_withdrawn(...)
    manually wherever a real withdrawal/deactivation actually happens
    in the app — see the bottom of this file.
  - guardian_phone comes from Student.parents (a M2M to ParentProfile),
    which may have zero, one, or several linked parents. This picks the
    first one's phone if present, else sends None. Adjust
    _guardian_phone_for() below if ParentProfile's phone field is named
    something other than "phone".
"""

from django.db.models.signals import post_save, m2m_changed
from django.db.transaction import on_commit
from django.dispatch import receiver

from . import publisher

STUDENT_MODEL_PATH = "students.Student"


def _get_current_term() -> str:
    from django.conf import settings
    return getattr(settings, "CURRENT_TERM", "T2-2025")


def _full_name(student) -> str:
    return f"{student.first_name} {student.last_name}".strip()


def _grade_name(student):
    return student.current_class.name if student.current_class_id else None


def _guardian_phone_for(student):
    parent = student.parents.first()
    if parent is None:
        return None
    # Adjust "phone" below if ParentProfile's field is named differently
    # (e.g. "phone_number", "contact_phone").
    return getattr(parent, "phone", None)


def _snapshot_kwargs(student):
    return dict(
        student_id=student.admission_no,
        name=_full_name(student),
        grade=_grade_name(student),
        guardian_phone=_guardian_phone_for(student),
        status=student.status.upper(),
    )


@receiver(post_save, sender=STUDENT_MODEL_PATH)
def on_student_saved(sender, instance, created, **kwargs):
    if created:
        kwargs_ = _snapshot_kwargs(instance)
        on_commit(lambda: publisher.student_enrolled(**kwargs_, term=_get_current_term()))
    else:
        kwargs_ = _snapshot_kwargs(instance)
        on_commit(lambda: publisher.student_updated(**kwargs_))


def on_student_parents_changed(sender, instance, action, **kwargs):
    """
    parents is a ManyToManyField, so post_save on Student fires before any
    parent gets linked — guardianPhone would be stale on a brand-new
    student's first save. This republishes an update once parents are
    actually attached/changed, so guardianPhone catches up.

    NOT auto-registered here (M2M signals need the through-model, which
    isn't available at import time). Wire it once in apps.py's ready():

        from django.db.models.signals import m2m_changed
        from students.models import Student
        from .signals import on_student_parents_changed
        m2m_changed.connect(on_student_parents_changed, sender=Student.parents.through)
    """
    if action in ("post_add", "post_remove", "post_clear"):
        kwargs_ = _snapshot_kwargs(instance)
        on_commit(lambda: publisher.student_updated(**kwargs_))


# Withdrawal: no status field exists to hook a signal to. Call this
# directly wherever a real withdrawal/deactivation happens in your app:
#
#     from student_sync import publisher
#     from datetime import date
#     publisher.student_withdrawn(student.admission_no, withdrawn_on=date.today())
