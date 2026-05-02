from django import forms
from .models import ExamType, Exam, ExamResult


class ExamTypeForm(forms.ModelForm):
    class Meta:
        model = ExamType
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "e.g. Mid-term, End-term"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control", "rows": 3
            }),
        }


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ["name", "exam_type", "term", "year", "date", "description"]
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "e.g. End of Term 1 2025"
            }),
            "exam_type": forms.Select(attrs={"class": "form-control"}),
            "term": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "e.g. Term 1"
            }),
            "year": forms.NumberInput(attrs={
                "class": "form-control", "placeholder": "e.g. 2025"
            }),
            "date": forms.DateInput(attrs={
                "type": "date", "class": "form-control"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control", "rows": 2
            }),
        }


class ExamResultForm(forms.ModelForm):
    class Meta:
        model = ExamResult
        fields = ["student", "score"]
        widgets = {
            "student": forms.Select(attrs={"class": "form-control"}),
            "score": forms.NumberInput(attrs={
                "class": "form-control", "step": "0.5", "min": "0", "max": "100"
            }),
        }