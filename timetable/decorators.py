from django.shortcuts import get_object_or_404
from students.models import Classroom


def can_manage_timetable(user, classroom_id):
    if not user.is_authenticated:
        return False

    if user.is_superuser or user.role in ["admin", "superadmin"]:
        return True

    if user.role == "teacher":
        classroom = get_object_or_404(Classroom, pk=classroom_id)
        return classroom.class_teacher_id == user.id

    return False