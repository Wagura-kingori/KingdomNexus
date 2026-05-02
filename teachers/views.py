from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from profiles.models import TeacherProfile
from academics.models import Subject, Enrollment
from students.models import Student, Classroom
from exams.models import Exam, ExamResult
from exams.forms import ExamForm
from teachers.models import TeacherSubjectAssignment
from payroll.decorators import teacher_required


# ─────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────
def get_teacher_or_404(user):
    return get_object_or_404(TeacherProfile, user=user)


def get_teacher_classrooms(teacher):
    """All classrooms this teacher has any assignment in."""
    return Classroom.objects.filter(
        subject_assignments__teacher=teacher
    ).distinct().select_related("class_grade", "section")


def get_class_teacher_classrooms(teacher):
    """Classrooms where this teacher IS the class teacher."""
    return Classroom.objects.filter(
        class_teacher=teacher.user
    ).select_related("class_grade", "section")


def is_class_teacher_of(teacher, classroom):
    return classroom.class_teacher_id == teacher.user_id


def get_assignment_or_403(teacher, assignment_id):
    """Subject teacher can only access their own assignment."""
    return get_object_or_404(
        TeacherSubjectAssignment,
        id=assignment_id,
        teacher=teacher
    )


# ─────────────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────────────
@login_required
@teacher_required
def teacher_dashboard(request):
    teacher = get_teacher_or_404(request.user)

    # All classrooms this teacher teaches in
    teaching_classrooms = get_teacher_classrooms(teacher)

    # All their subject assignments grouped by classroom
    assignments = (
        TeacherSubjectAssignment.objects
        .filter(teacher=teacher)
        .select_related("subject", "classroom__class_grade", "classroom__section")
        .order_by("classroom__class_grade__name", "classroom__section__name", "subject__name")
    )

    # Classrooms where they are class teacher
    class_teacher_rooms = get_class_teacher_classrooms(teacher)

    return render(request, "teachers/dashboard.html", {
        "teacher": teacher,
        "school": teacher.school,
        "assignments": assignments,
        "teaching_classrooms": teaching_classrooms,
        "class_teacher_rooms": class_teacher_rooms,
        "is_class_teacher": teacher.is_class_teacher,
    })


# ─────────────────────────────────────────────────
#  SUBJECT STUDENTS  (per assignment)
# ─────────────────────────────────────────────────
@login_required
@teacher_required
def teacher_subject_students(request, assignment_id):
    teacher = get_teacher_or_404(request.user)
    assignment = get_assignment_or_403(teacher, assignment_id)

    classroom = assignment.classroom
    subject   = assignment.subject

    # Students in this classroom enrolled in this subject
    students = Student.objects.filter(
        current_class=classroom.class_grade,
        current_section=classroom.section,
        school=teacher.school,
        enrollments__subjects=subject
    ).distinct().order_by("last_name", "first_name")

    return render(request, "teachers/subject_students.html", {
        "teacher":    teacher,
        "school":     teacher.school,
        "assignment": assignment,
        "classroom":  classroom,
        "subject":    subject,
        "students":   students,
    })


# ─────────────────────────────────────────────────
#  EXAMS & RESULTS  (per assignment)
# ─────────────────────────────────────────────────
@login_required
@teacher_required
def teacher_subject_results(request, assignment_id):
    teacher = get_teacher_or_404(request.user)
    assignment = get_assignment_or_403(teacher, assignment_id)

    classroom = assignment.classroom
    subject   = assignment.subject

    students = Student.objects.filter(
        current_class=classroom.class_grade,
        current_section=classroom.section,
        school=teacher.school
    ).order_by("last_name", "first_name")

    exams = Exam.objects.all().order_by("-year", "term")

    # Build results matrix {exam_id: {student_id: ExamResult}}
    results_map = {}
    for exam in exams:
        results_map[exam.id] = {
            r.student_id: r
            for r in ExamResult.objects.filter(
                exam=exam,
                student__in=students,
                subject=subject
            ).select_related("student")
        }

    return render(request, "teachers/subject_exams.html", {
        "teacher":         teacher,
        "school":          teacher.school,
        "assignment":      assignment,
        "classroom":       classroom,
        "subject":         subject,
        "enrolled_students": students,
        "exams":           exams,
        "results_map":     results_map,
    })


# ─────────────────────────────────────────────────
#  ENTER / EDIT RESULTS  (per assignment + exam)
# ─────────────────────────────────────────────────
@login_required
@teacher_required
def teacher_enter_results(request, assignment_id, exam_id):
    teacher = get_teacher_or_404(request.user)
    assignment = get_assignment_or_403(teacher, assignment_id)

    classroom = assignment.classroom
    subject   = assignment.subject
    exam      = get_object_or_404(Exam, id=exam_id)

    students = Student.objects.filter(
        current_class=classroom.class_grade,
        current_section=classroom.section,
        school=teacher.school
    ).order_by("last_name", "first_name")

    existing = {
        r.student_id: r
        for r in ExamResult.objects.filter(
            exam=exam, student__in=students, subject=subject
        )
    }

    if request.method == "POST":
        saved  = 0
        errors = []

        with transaction.atomic():
            for student in students:
                raw = request.POST.get(f"score_{student.id}", "").strip()
                if raw == "":
                    continue
                try:
                    score = float(raw)
                    if not (0 <= score <= 100):
                        raise ValueError
                except ValueError:
                    errors.append(
                        f"{student.first_name} {student.last_name}: "
                        f"invalid score '{raw}'"
                    )
                    continue

                result = existing.get(student.id)
                if result:
                    result.score = score
                    result.save()
                else:
                    ExamResult.objects.create(
                        exam=exam,
                        student=student,
                        subject=subject,
                        score=score
                    )
                saved += 1

        for e in errors:
            messages.error(request, e)
        if saved:
            messages.success(request, f"{saved} result(s) saved.")

        return redirect("teachers:enter_results",
                        assignment_id=assignment_id, exam_id=exam_id)

    rows = [{"student": s, "result": existing.get(s.id)} for s in students]

    return render(request, "teachers/enter_results.html", {
        "teacher":    teacher,
        "school":     teacher.school,
        "assignment": assignment,
        "classroom":  classroom,
        "subject":    subject,
        "exam":       exam,
        "rows":       rows,
    })


# ─────────────────────────────────────────────────
#  CLASS TEACHER — VIEW ALL SUBJECTS IN A CLASSROOM
# ─────────────────────────────────────────────────
@login_required
@teacher_required
def class_teacher_classroom(request, classroom_id):
    teacher  = get_teacher_or_404(request.user)
    classroom = get_object_or_404(Classroom, id=classroom_id)

    # Only the class teacher of this room or a superadmin can access
    if not is_class_teacher_of(teacher, classroom) and not request.user.is_superadmin():
        messages.error(request, "You are not the class teacher of this classroom.")
        return redirect("teachers:dashboard")

    # All subject assignments for this classroom
    assignments = (
        TeacherSubjectAssignment.objects
        .filter(classroom=classroom)
        .select_related("subject", "teacher__user")
        .order_by("subject__name")
    )

    students = Student.objects.filter(
        current_class=classroom.class_grade,
        current_section=classroom.section,
        school=teacher.school
    ).order_by("last_name", "first_name")

    exams = Exam.objects.all().order_by("-year", "term")

    return render(request, "teachers/class_teacher_view.html", {
        "teacher":     teacher,
        "school":      teacher.school,
        "classroom":   classroom,
        "assignments": assignments,
        "students":    students,
        "exams":       exams,
    })


# ─────────────────────────────────────────────────
#  CLASS TEACHER — ASSIGN SUBJECT TO TEACHER
# ─────────────────────────────────────────────────
@login_required
@teacher_required
def assign_subject(request, classroom_id):
    teacher  = get_teacher_or_404(request.user)
    classroom = get_object_or_404(Classroom, id=classroom_id)

    if not is_class_teacher_of(teacher, classroom) and not request.user.is_superadmin():
        messages.error(request, "Only the class teacher can assign subjects.")
        return redirect("teachers:dashboard")

    # Teachers in the same school
    school_teachers = TeacherProfile.objects.filter(
        school=teacher.school
    ).select_related("user")

    subjects = Subject.objects.filter(school=teacher.school)

    if request.method == "POST":
        subject_id    = request.POST.get("subject")
        assignee_id   = request.POST.get("teacher")

        subject  = get_object_or_404(Subject, id=subject_id, school=teacher.school)
        assignee = get_object_or_404(TeacherProfile, id=assignee_id, school=teacher.school)

        obj, created = TeacherSubjectAssignment.objects.get_or_create(
            teacher=assignee,
            subject=subject,
            classroom=classroom,
            defaults={"school": teacher.school}
        )
        if created:
            messages.success(
                request,
                f"{subject.name} assigned to "
                f"{assignee.user.get_full_name()} for {classroom}."
            )
        else:
            messages.warning(request, "This assignment already exists.")

        return redirect("teachers:class_teacher_view", classroom_id=classroom_id)

    return render(request, "teachers/assign_subject.html", {
        "teacher":         teacher,
        "school":          teacher.school,
        "classroom":       classroom,
        "school_teachers": school_teachers,
        "subjects":        subjects,
    })


# ─────────────────────────────────────────────────
#  CREATE EXAM  (teacher portal wrapper)
# ─────────────────────────────────────────────────
@login_required
@teacher_required
def teacher_create_exam(request, assignment_id):
    teacher    = get_teacher_or_404(request.user)
    assignment = get_assignment_or_403(teacher, assignment_id)

    form = ExamForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"Exam '{form.cleaned_data['name']}' created.")
        return redirect("teachers:subject_exams", assignment_id=assignment_id)

    return render(request, "teachers/create_exam.html", {
        "teacher":    teacher,
        "school":     teacher.school,
        "assignment": assignment,
        "subject":    assignment.subject,
        "classroom":  assignment.classroom,
        "form":       form,
    })