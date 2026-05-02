from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.forms import modelformset_factory

from .models import ExamType, Exam, ExamResult
from .forms import ExamTypeForm, ExamForm, ExamResultForm
from academics.models import Subject          
from students.models import Student


ExamResultFormSet = modelformset_factory(
    ExamResult,
    form=ExamResultForm,
    extra=0
)


# ── EXAM TYPES ──────────────────────────────
def exam_types_list(request):
    exam_types = ExamType.objects.all()
    return render(request, "exams/exam_types_list.html", {"exam_types": exam_types})


def exam_type_create(request):
    if request.method == "POST":
        form = ExamTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam type added successfully.")
            return redirect("exams:exam_types_list")
    else:
        form = ExamTypeForm()
    return render(request, "exams/exam_type_form.html", {"form": form})


def exam_types_form(request, id=None):
    instance = ExamType() if id is None else get_object_or_404(ExamType, id=id)
    if request.method == "POST":
        instance.name = request.POST.get("name")
        instance.save()
        return redirect("exams:exam_types_list")
    return render(request, "exams/exam_types_form.html", {"type": instance})


# ── EXAMS ────────────────────────────────────
def exams_list(request):
    exams = Exam.objects.select_related("exam_type").order_by("-year", "term")
    return render(request, "exams/exams_list.html", {"exams": exams})


def exam_create(request):
    if request.method == "POST":
        form = ExamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exam created successfully.")
            return redirect("exams:exams_list")
    else:
        form = ExamForm()
    return render(request, "exams/exam_form.html", {"form": form})


def exams_form(request, id=None):
    instance = Exam() if id is None else get_object_or_404(Exam, id=id)
    types = ExamType.objects.all()

    if request.method == "POST":
        instance.exam_type_id = request.POST.get("exam_type")
        instance.name         = request.POST.get("name")
        instance.term         = request.POST.get("term")
        instance.year         = request.POST.get("year")
        instance.date         = request.POST.get("date") or None
        instance.save()
        return redirect("exams:exams_list")

    return render(request, "exams/exams_form.html", {
        "exam": instance,
        "types": types,
    })


# ── RESULTS ──────────────────────────────────
def results_list(request):
    results = ExamResult.objects.select_related(
        "exam", "student"
    ).order_by("-exam__year", "student__last_name")
    return render(request, "exams/results_list.html", {"results": results})


def results_form(request, id=None):
    instance = ExamResult() if id is None else get_object_or_404(ExamResult, id=id)
    exams    = Exam.objects.all()
    students = Student.objects.all()

    if request.method == "POST":
        instance.exam_id    = request.POST.get("exam")
        instance.student_id = request.POST.get("student")
        instance.score      = request.POST.get("score")
        instance.save()
        return redirect("exams:results_list")

    return render(request, "exams/results_form.html", {
        "result":   instance,
        "exams":    exams,
        "students": students,
    })


def student_results(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    results = ExamResult.objects.filter(
        student=student
    ).select_related("exam", "exam__exam_type").order_by("-exam__year")
    return render(request, "exams/student_results.html", {
        "student": student,
        "results": results,
    })


def class_ranking(request, exam_id):
    exam    = get_object_or_404(Exam, id=exam_id)
    ranking = ExamResult.objects.filter(
        exam=exam
    ).select_related("student").order_by("position")
    return render(request, "exams/class_ranking.html", {
        "exam":    exam,
        "ranking": ranking,
    })


# ── BULK RESULTS ENTRY (admin use) ───────────
def exam_results_entry(request, exam_id):
    """
    Admin-side bulk entry for an entire exam.
    Teacher-side entry is handled by teachers.views.teacher_enter_results
    which filters by subject enrollment.
    """
    exam     = get_object_or_404(Exam, id=exam_id)
    students = Student.objects.all().order_by("last_name", "first_name")

    # Pre-create blank results for any student that doesn't have one yet
    for student in students:
        ExamResult.objects.get_or_create(
            exam=exam,
            student=student,
            defaults={"score": 0}
        )

    queryset = ExamResult.objects.filter(exam=exam).select_related("student")

    if request.method == "POST":
        formset = ExamResultFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Results saved successfully.")
            return redirect("exams:exams_list")
    else:
        formset = ExamResultFormSet(queryset=queryset)

    return render(request, "exams/exam_results_entry.html", {
        "exam":    exam,
        "formset": formset,
    })