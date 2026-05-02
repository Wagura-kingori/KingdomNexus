from django.db import models
from students.models import Student
from django.conf import settings
from academics.models import Classroom
from django.utils import timezone
from schools.models import School
school = models.ForeignKey(School, on_delete=models.CASCADE)
class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('present','Present'),('absent','Absent'),('late','Late')])
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('student','date')



class Attendance(models.Model):
    ATTENDANCE_STATUS = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=ATTENDANCE_STATUS)
    remarks = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('student', 'date')  # one attendance per student per day
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.full_name} - {self.date} ({self.status})"
