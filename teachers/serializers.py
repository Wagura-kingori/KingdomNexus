from rest_framework import serializers
from .models import Teacher
from academics.serializers import SubjectSerializer


class TeacherSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    assigned_subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'name', 'staff_id', 'phone', 'assigned_subjects']

    def get_name(self, obj):
        return obj.user.get_full_name() or obj.user.username