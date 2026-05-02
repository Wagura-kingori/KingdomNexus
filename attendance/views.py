from rest_framework import viewsets
from .models import AttendanceRecord
from .serializers import AttendanceRecordSerializer
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from .models import Attendance
from .forms import AttendanceForm
from students.models import Student
from academics.models import Classroom
from datetime import date

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]




def attendance_list(request):
    records = Attendance.objects.all()
    return render(request, 'attendance/attendance_list.html', {'records': records})


def attendance_take(request, class_id):
    classroom = Classroom.objects.get(id=class_id)
    students = Student.objects.filter(classroom=classroom)

    if request.method == "POST":
        for student in students:
            status = request.POST.get(f"status_{student.id}")
            remarks = request.POST.get(f"remarks_{student.id}", "")
            Attendance.objects.update_or_create(
                student=student,
                date=date.today(),
                defaults={
                    'classroom': classroom,
                    'status': status,
                    'remarks': remarks
                }
            )
        return redirect('attendance_list')

    return render(request, 'attendance/take_attendance.html', {
        'classroom': classroom,
        'students': students,
    })
