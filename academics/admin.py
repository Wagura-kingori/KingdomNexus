# academics/admin.py
from django.contrib import admin
from .models import Subject, Enrollment

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_grade', 'section']
