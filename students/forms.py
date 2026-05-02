from django import forms
from .models import Student
from django.contrib.auth import get_user_model
from profiles.models import ParentProfile

User = get_user_model()

class ParentProfileForm(forms.ModelForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = ParentProfile
        fields = ['occupation', 'phone']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if commit:
            profile.save()
            profile.user.email = self.cleaned_data.get('email')
            profile.user.save()
        return profile


class StudentForm(forms.ModelForm):
    parents = forms.ModelMultipleChoiceField(
        queryset=ParentProfile.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'current_class', 'current_section', 'parents']

