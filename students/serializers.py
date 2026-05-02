from rest_framework import serializers
from .models import Student, ClassGrade, Section
from profiles.models import ParentProfile

class ClassGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGrade
        fields = ['id', 'name']

class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name', 'class_grade']

class ParentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentProfile
        fields = ['id', 'user']

class StudentSerializer(serializers.ModelSerializer):
    parents = ParentProfileSerializer(many=True, read_only=True)
    class Meta:
        model = Student
        fields = ['id', 'first_name', 'last_name', 'dob', 'gender', 'admission_no', 'current_class', 'current_section', 'parents']
