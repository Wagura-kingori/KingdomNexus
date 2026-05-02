from rest_framework import viewsets
from .models import Student, ClassGrade, Section
from profiles.models import ParentProfile
from .serializers import StudentSerializer, ClassGradeSerializer, SectionSerializer, ParentProfileSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from .forms import StudentForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
import json

from schools.models import School
from .models import ClassGrade, Section




def _school_access(request, school):
    """Return True if the request user may manage this school."""
    return request.user.is_superadmin() or request.user.school == school


# ─────────────────────────────────────────────
#  MAIN PAGE
# ─────────────────────────────────────────────
@login_required
def manage_grades(request, school_id):
    school = get_object_or_404(School, id=school_id)
    if not _school_access(request, school):
        messages.error(request, "Access denied.")
        from django.shortcuts import redirect
        return redirect("home")

    grades = ClassGrade.objects.filter(school=school).prefetch_related("sections")

    total_sections = sum(g.sections.count() for g in grades)

    return render(request, "students/manage_grades.html", {
        "school":          school,
        "grades":          grades,
        "total_sections":  total_sections,
    })


# ─────────────────────────────────────────────
#  GRADE CRUD
# ─────────────────────────────────────────────
@login_required
@require_POST
def grade_create(request, school_id):
    school = get_object_or_404(School, id=school_id)
    if not _school_access(request, school):
        return JsonResponse({"success": False, "error": "Access denied."}, status=403)

    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    name = (data.get("name") or "").strip()
    if not name:
        return JsonResponse({"success": False, "error": "Grade name is required."})

    if ClassGrade.objects.filter(school=school, name__iexact=name).exists():
        return JsonResponse({"success": False, "error": f'"{name}" already exists.'})

    grade = ClassGrade.objects.create(school=school, name=name)
    return JsonResponse({"success": True, "id": grade.id, "name": grade.name, "section_count": 0})


@login_required
@require_POST
def grade_update(request, grade_id):
    grade = get_object_or_404(ClassGrade, id=grade_id)
    if not _school_access(request, grade.school):
        return JsonResponse({"success": False, "error": "Access denied."}, status=403)

    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    name = (data.get("name") or "").strip()
    if not name:
        return JsonResponse({"success": False, "error": "Grade name is required."})

    if ClassGrade.objects.filter(school=grade.school, name__iexact=name).exclude(pk=grade.pk).exists():
        return JsonResponse({"success": False, "error": f'"{name}" already exists.'})

    grade.name = name
    grade.save()
    return JsonResponse({"success": True, "id": grade.id, "name": grade.name})


@login_required
@require_POST
def grade_delete(request, grade_id):
    grade = get_object_or_404(ClassGrade, id=grade_id)
    if not _school_access(request, grade.school):
        return JsonResponse({"success": False, "error": "Access denied."}, status=403)

    section_count = grade.sections.count()
    name = grade.name
    grade.delete()
    return JsonResponse({"success": True, "name": name, "section_count": section_count})


# ─────────────────────────────────────────────
#  SECTION CRUD
# ─────────────────────────────────────────────
@login_required
@require_POST
def section_create(request, grade_id):
    grade = get_object_or_404(ClassGrade, id=grade_id)
    if not _school_access(request, grade.school):
        return JsonResponse({"success": False, "error": "Access denied."}, status=403)

    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    name = (data.get("name") or "").strip()
    if not name:
        return JsonResponse({"success": False, "error": "Section name is required."})

    if Section.objects.filter(school=grade.school, class_grade=grade, name__iexact=name).exists():
        return JsonResponse({"success": False, "error": f'"{name}" already exists in this grade.'})

    section = Section.objects.create(school=grade.school, class_grade=grade, name=name)
    return JsonResponse({
        "success":  True,
        "id":       section.id,
        "name":     section.name,
        "grade_id": grade.id,
        "grade_name": grade.name,
    })


@login_required
@require_POST
def section_update(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    if not _school_access(request, section.school):
        return JsonResponse({"success": False, "error": "Access denied."}, status=403)

    try:
        data = json.loads(request.body)
    except ValueError:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    name = (data.get("name") or "").strip()
    if not name:
        return JsonResponse({"success": False, "error": "Section name is required."})

    if Section.objects.filter(
        school=section.school, class_grade=section.class_grade, name__iexact=name
    ).exclude(pk=section.pk).exists():
        return JsonResponse({"success": False, "error": f'"{name}" already exists in this grade.'})

    section.name = name
    section.save()
    return JsonResponse({"success": True, "id": section.id, "name": section.name})


@login_required
@require_POST
def section_delete(request, section_id):
    section = get_object_or_404(Section, id=section_id)
    if not _school_access(request, section.school):
        return JsonResponse({"success": False, "error": "Access denied."}, status=403)

    name = section.name
    grade_id = section.class_grade_id
    section.delete()
    return JsonResponse({"success": True, "name": name, "grade_id": grade_id})


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class ClassGradeViewSet(viewsets.ModelViewSet):
    queryset = ClassGrade.objects.all()
    serializer_class = ClassGradeSerializer
    permission_classes = [IsAuthenticated]

class SectionViewSet(viewsets.ModelViewSet):
    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated]

class ParentProfileViewSet(viewsets.ModelViewSet):
    queryset = ParentProfile.objects.all()
    serializer_class = ParentProfileSerializer
    permission_classes = [IsAuthenticated]


def student_list(request):
    students = Student.objects.all()
    return render(request, 'students/student_list.html', {'students': students})

def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('students:student_list')
    else:
        form = StudentForm()
    return render(request, 'students/add_student.html', {'form': form})

def edit_student(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            return redirect('students:student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/edit_student.html', {'form': form, 'student': student})
