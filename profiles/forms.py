from django import forms
from .models import TeacherProfile, ParentProfile, PayrollProfile


class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ["department", "is_class_teacher", "subjects"]
        widgets = {
            "department": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Mathematics"
            }),
            "is_class_teacher": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
            "subjects": forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            "subjects": "Select all subjects you teach.",
        }


class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ["occupation", "phone"]
        widgets = {
            "occupation": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Accountant"
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. +254 700 000 000"
            }),
        }


class PayrollProfileForm(forms.ModelForm):
    class Meta:
        model = PayrollProfile
        fields = ["bank_name", "bank_account"]
        widgets = {
            "bank_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Equity Bank"
            }),
            "bank_account": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Account number"
            }),
        }