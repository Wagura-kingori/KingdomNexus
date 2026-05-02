from datetime import datetime, timedelta, date, time
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from students.models import Classroom
from profiles.models import TeacherProfile
from teachers.models import TeacherSubjectAssignment

from .models import (
    TimetableSetting,
    TimetableEntry,
    SubjectRule,
)

from .decorators import can_manage_timetable


# ------------------------------------------------
# Setup Timetable
# ------------------------------------------------
@login_required
def setup_timetable(request, classroom_id):
    classroom = get_object_or_404(Classroom, pk=classroom_id)

    if not can_manage_timetable(request.user, classroom_id):
        messages.error(request, "Access denied.")
        return redirect("teachers:dashboard")

    setting, _ = TimetableSetting.objects.get_or_create(
        school=request.user.school,
        classroom=classroom,
        defaults={
            "days": [
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
            ]
        }
    )

    assignments = TeacherSubjectAssignment.objects.filter(
        classroom=classroom
    ).select_related("subject", "teacher__user")

    if request.method == "POST":
        for a in assignments:
            count = int(request.POST.get(f"subject_{a.subject.id}", 4))

            SubjectRule.objects.update_or_create(
                setting=setting,
                subject=a.subject,
                defaults={"weekly_lessons": count}
            )

        messages.success(request, "Saved successfully.")
        return redirect("timetable:view", classroom_id=classroom.id)

    existing = {
        x.subject_id: x.weekly_lessons
        for x in setting.subject_rules.all()
    }

    return render(request, "timetable/setup.html", {
        "classroom": classroom,
        "setting": setting,
        "assignments": assignments,
        "existing": existing,
    })


# ------------------------------------------------
# View Timetable
# ------------------------------------------------
@login_required
def view_timetable(request, classroom_id):
    classroom = get_object_or_404(Classroom, pk=classroom_id)

    entries = TimetableEntry.objects.filter(
        classroom=classroom
    ).select_related("subject", "teacher__user")

    return render(request, "timetable/view.html", {
        "classroom": classroom,
        "entries": entries,
    })

@login_required
def timetable_list(request):
    classrooms = Classroom.objects.filter(
        school=request.user.school
    )

    return render(request, "timetable/list.html", {
        "classrooms": classrooms
    })
# ------------------------------------------------
# Teacher Workload
# ------------------------------------------------
@login_required
def teacher_workload(request):
    teacher = get_object_or_404(
        TeacherProfile,
        user=request.user
    )

    entries = TimetableEntry.objects.filter(
        teacher=teacher
    ).select_related(
        "classroom__class_grade",
        "classroom__section",
        "subject"
    )

    return render(request, "timetable/teacher_workload.html", {
        "entries": entries,
        "teacher": teacher,
    })
@login_required
def generate_timetable(request, classroom_id):
    classroom = get_object_or_404(Classroom, pk=classroom_id)

    if not can_manage_timetable(request.user, classroom_id):
        messages.error(request, "Access denied.")
        return redirect("teachers:dashboard")

    setting = get_object_or_404(
        TimetableSetting,
        classroom=classroom
    )

    TimetableEntry.objects.filter(
        classroom=classroom
    ).delete()

    start_dt = datetime.combine(date.today(), setting.start_time)
    end_dt = datetime.combine(date.today(), setting.end_time)

    slot_minutes = setting.lesson_minutes
    days = setting.days

    # build daily time slots
    slots = []
    current = start_dt

    while current + timedelta(minutes=slot_minutes) <= end_dt:
        nxt = current + timedelta(minutes=slot_minutes)
        slots.append((current.time(), nxt.time()))
        current = nxt

    rules = list(setting.subject_rules.all().select_related("subject"))

    if not rules:
        messages.error(request, "Please setup subjects first.")
        return redirect("timetable:setup", classroom_id=classroom.id)

    # Expand subjects by weekly count
    lesson_pool = []
    for r in rules:
        for i in range(r.weekly_lessons):
            lesson_pool.append(r.subject)

    # Spread evenly
    day_index = 0
    slot_index = 0

    for subject in lesson_pool:
        assigned = TeacherSubjectAssignment.objects.filter(
            classroom=classroom,
            subject=subject
        ).select_related("teacher").first()

        teacher = assigned.teacher if assigned else None

        if day_index >= len(days):
            day_index = 0
            slot_index += 1

        if slot_index >= len(slots):
            break

        start_time, end_time = slots[slot_index]

        TimetableEntry.objects.create(
            setting=setting,
            classroom=classroom,
            subject=subject,
            teacher=teacher,
            day=days[day_index],
            start_time=start_time,
            end_time=end_time,
        )

        day_index += 1

    messages.success(request, "Timetable generated successfully.")
    return redirect("timetable:view", classroom_id=classroom.id)