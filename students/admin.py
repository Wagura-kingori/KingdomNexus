

from django.contrib import admin
from .models import ClassGrade, Section, Student
from .models import ClassGrade, Section, Student
from profiles.models import ParentProfile
@admin.register(ClassGrade)
class ClassGradeAdmin(admin.ModelAdmin):
    list_display = ['name']  # adjust fields

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'class_grade']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'current_class', 'current_section']

@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']  # adjust fields

