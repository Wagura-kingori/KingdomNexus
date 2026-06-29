from django.contrib import admin
from .models import (
    Room,
    TimetableSetting,
    TimetableBreak,
    SubjectConfiguration,
    ClassroomTimetable,
    TimetableEntry,
    MasterTimetableEntry,
    ClassroomTimetableEntry,
)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'room_type', 'capacity']
    list_filter = ['school', 'room_type']
    search_fields = ['name']


class TimetableBreakInline(admin.TabularInline):
    model = TimetableBreak
    extra = 1


class SubjectConfigInline(admin.TabularInline):
    model = SubjectConfiguration
    extra = 1


@admin.register(TimetableSetting)
class TimetableSettingAdmin(admin.ModelAdmin):
    list_display = ['classroom', 'start_time', 'end_time', 'lesson_duration']
    inlines = [TimetableBreakInline, SubjectConfigInline]


@admin.register(ClassroomTimetable)
class ClassroomTimetableAdmin(admin.ModelAdmin):
    list_display = ['classroom', 'academic_year', 'status', 'created_by', 'updated_at']
    list_filter = ['status', 'academic_year']
    search_fields = ['classroom__class_grade__name']


@admin.register(MasterTimetableEntry)
class MasterTimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'classroom', 'room', 'day', 'start_time', 'end_time', 'academic_year']
    list_filter = ['day', 'academic_year', 'school']
    search_fields = ['teacher__user__first_name', 'subject__name', 'classroom__class_grade__name']
    ordering = ['day', 'start_time']


@admin.register(ClassroomTimetableEntry)
class ClassroomTimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['timetable', 'subject', 'teacher', 'room', 'day', 'start_time', 'end_time']
    list_filter = ['day', 'timetable__academic_year']
    search_fields = ['subject__name', 'teacher__user__first_name']


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ['classroom', 'subject', 'teacher', 'day', 'start_time', 'end_time', 'room']
    list_filter = ['day', 'classroom']
    search_fields = ['subject__name', 'teacher__user__first_name']