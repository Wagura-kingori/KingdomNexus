from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from students.models import  Student
from profiles.models import ParentProfile
from exams.models import ExamResult
from attendance.models import Attendance
from fees.models import Fee, Payment
from messaging.models import Notice
from payroll.decorators import parent_required


@login_required
@parent_required
def parent_dashboard(request):
    parent = get_object_or_404(ParentProfile, user=request.user)
    children = Student.objects.filter(parents=parent).select_related('school')

    return render(request, "parents/parent_dashboard.html", {
        "parent": parent,
        "children": children
    })


@login_required
@parent_required
def parent_children(request):
    parent = get_object_or_404(ParentProfile, user=request.user)
    children = Student.objects.filter(parents=parent)

    return render(request, "parents/children_list.html", {"children": children})


@login_required
@parent_required
def parent_child_detail(request, child_id):
    parent = get_object_or_404(ParentProfile, user=request.user)
    child = get_object_or_404(Student, id=child_id, parents=parent)

    return render(request, "parents/parent_child_detail.html", {"child": child})


@login_required
@parent_required
def parent_child_results(request, child_id):
    parent = get_object_or_404(ParentProfile, user=request.user)
    child = get_object_or_404(Student, id=child_id, parents=parent)

    results = ExamResult.objects.filter(student=child)

    return render(request, "parents/parent_child_results.html", {
        "child": child,
        "results": results
    })


@login_required
@parent_required
def parent_child_attendance(request, child_id):
    parent = get_object_or_404(ParentProfile, user=request.user)
    child = get_object_or_404(Student, id=child_id, parents=parent)

    attendance = Attendance.objects.filter(student=child)

    return render(request, "parents/parent_child_attendance.html", {
        "child": child,
        "attendance": attendance
    })


@login_required
@parent_required
def parent_child_fees(request, child_id):
    parent = get_object_or_404(ParentProfile, user=request.user)
    child = get_object_or_404(Student, id=child_id, parents=parent)

    fee = Fee.objects.filter(student=child).first()
    payments = Payment.objects.filter(student=child)

    return render(request, "parents/parent_child_fees.html", {
        "child": child,
        "fee": fee,
        "payments": payments
    })


@login_required
@parent_required
def parent_notifications(request):
    parent = get_object_or_404(ParentProfile, user=request.user)

    children = Student.objects.filter(parents=parent)
    notices = Notice.objects.filter(
        classroom__school__in=children.values_list("school", flat=True)
    ).distinct()

    return render(request, "parents/parent_notifications.html", {
        "notices": notices
    })
