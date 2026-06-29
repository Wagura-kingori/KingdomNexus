from rest_framework import serializers
from .models import (
    Room,
    MasterTimetableEntry,
    ClassroomTimetable,
    ClassroomTimetableEntry,
    Period,
    TimetableGenerationConfig,
    GenerationBreak,
    ClassroomSubjectConfig,
    TimetableGenerationJob,
)


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name', 'capacity', 'room_type', 'school']


class MasterTimetableEntrySerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    classroom_name = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()

    class Meta:
        model = MasterTimetableEntry
        fields = [
            'id', 'school', 'teacher', 'teacher_name',
            'subject', 'subject_name', 'classroom', 'classroom_name',
            'room', 'room_name', 'day', 'start_time', 'end_time',
            'academic_year',
        ]
        extra_kwargs = {
            'school': {'required': False, 'allow_null': True},
        }

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() or obj.teacher.user.username

    def get_subject_name(self, obj):
        return obj.subject.name

    def get_classroom_name(self, obj):
        return str(obj.classroom)

    def get_room_name(self, obj):
        return obj.room.name if obj.room else None


class ClassroomTimetableSerializer(serializers.ModelSerializer):
    classroom_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassroomTimetable
        fields = [
            'id', 'classroom', 'classroom_name',
            'academic_year', 'status', 'created_by',
            'created_at', 'updated_at',
        ]

    def get_classroom_name(self, obj):
        return str(obj.classroom)


class ClassroomTimetableEntrySerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    room_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassroomTimetableEntry
        fields = [
            'id', 'timetable', 'master_entry',
            'subject', 'subject_name', 'teacher', 'teacher_name',
            'room', 'room_name', 'day', 'start_time', 'end_time',
            'is_break', 'break_name',
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() or obj.teacher.user.username

    def get_subject_name(self, obj):
        return obj.subject.name

    def get_room_name(self, obj):
        return obj.room.name if obj.room else None


class PeriodSerializer(serializers.ModelSerializer):
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = Period
        fields = ['id', 'name', 'start_time', 'end_time', 'is_break', 'school', 'duration_minutes']
        extra_kwargs = {
            'school': {'required': False, 'allow_null': True},
        }

    def get_duration_minutes(self, obj):
        start = obj.start_time.hour * 60 + obj.start_time.minute
        end = obj.end_time.hour * 60 + obj.end_time.minute
        return end - start


class GenerationBreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = GenerationBreak
        fields = ['id', 'config', 'name', 'start_time', 'end_time']
        extra_kwargs = {'config': {'required': False}}


class ClassroomSubjectConfigSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    classroom_name = serializers.SerializerMethodField()

    class Meta:
        model = ClassroomSubjectConfig
        fields = [
            'id', 'config', 'classroom', 'classroom_name',
            'subject', 'subject_name',
            'teacher', 'teacher_name',
            'lessons_per_week', 'is_fixed',
            'fixed_day', 'fixed_start_time', 'fixed_scope',
        ]

    def get_teacher_name(self, obj):
        return obj.teacher.user.get_full_name() or obj.teacher.user.username

    def get_classroom_name(self, obj):
        return str(obj.classroom)


class TimetableGenerationConfigSerializer(serializers.ModelSerializer):
    breaks = GenerationBreakSerializer(many=True, read_only=True)
    subject_configs = ClassroomSubjectConfigSerializer(many=True, read_only=True)

    class Meta:
        model = TimetableGenerationConfig
        fields = [
            'id', 'school', 'academic_year',
            'lesson_duration', 'school_start_time', 'school_end_time',
            'days', 'breaks', 'subject_configs', 'created_at',
        ]
        extra_kwargs = {
            'school': {'required': False, 'allow_null': True},
        }


class TimetableGenerationJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimetableGenerationJob
        fields = [
            'id', 'school', 'academic_year', 'status',
            'task_id', 'started_at', 'completed_at',
            'error_message', 'entries_created', 'conflicts',
        ]