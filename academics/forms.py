from django import forms
from .models import Subject, Enrollment

class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ["name", "code"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "code": forms.TextInput(attrs={"class": "form-control"}),
        }

class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ['student', 'class_grade', 'section', 'subjects']
        widgets = {
            'subjects': forms.CheckboxSelectMultiple
        }


