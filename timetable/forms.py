from django import forms
from .models import Period, TimetableEntry
from academics.models import Subject
from users.models import User
from students.models import Classroom


class PeriodForm(forms.ModelForm):
    class Meta:
        model = Period
        fields = ['name', 'start_time', 'end_time']


class TimetableEntryForm(forms.ModelForm):
    class Meta:
        model = TimetableEntry
        fields = ['classroom', 'subject', 'teacher', 'day', 'period']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        
        self.fields['teacher'].queryset = User.objects.filter(role='teacher')
