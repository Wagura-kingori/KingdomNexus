from rest_framework import serializers
from .models import TeacherProfile
from academics.serializers import SubjectSerializer


class TeacherProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = TeacherProfile
        fields = ['id', 'name', 'employee_number', 'department', 'is_class_teacher', 'subjects']

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username