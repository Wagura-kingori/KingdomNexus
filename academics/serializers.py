from rest_framework import serializers
from .models import Subject, Enrollment


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'code', 'school']


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'class_grade', 'section', 'subjects', 'date_enrolled']