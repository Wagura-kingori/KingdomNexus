from django import forms
from django.forms import inlineformset_factory
from teachers.models import TeacherSubjectAssignment
from .models import SubjectConfiguration

from .models import (
    TimetableSetting,
    TimetableBreak,
    SubjectConfiguration,
)


class TimetableSettingForm(forms.ModelForm):
    days = forms.MultipleChoiceField(
        choices=[
            ("Monday", "Monday"),
            ("Tuesday", "Tuesday"),
            ("Wednesday", "Wednesday"),
            ("Thursday", "Thursday"),
            ("Friday", "Friday"),
            ("Saturday", "Saturday"),
        ],
        widget=forms.CheckboxSelectMultiple,
        initial=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
        ]
    )

    class Meta:
        model = TimetableSetting
        fields = [
            "start_time",
            "end_time",
            "lesson_duration",
            "days",
            "spread_lessons_evenly",
            "auto_generate",
        ]

        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class SubjectConfigurationForm(forms.ModelForm):

    class Meta:
        model = SubjectConfiguration
        fields = [
            "subject",
            "teacher_assignment",
            "lessons_per_week",
            "is_fixed",
            "fixed_day",
            "fixed_start_time",
        ]

    def __init__(self, *args, **kwargs):
        classroom = kwargs.pop("classroom", None)
        super().__init__(*args, **kwargs)

        # SUBJECT dropdown
        if classroom:
            self.fields["subject"].queryset = (
                TeacherSubjectAssignment.objects.filter(
                    classroom=classroom
                ).values_list("subject", flat=False).distinct()
            )

        # teacher initially empty (JS will fill it)
        self.fields["teacher_assignment"].queryset = TeacherSubjectAssignment.objects.none()


class TimetableBreakForm(forms.ModelForm):

    class Meta:
        model = TimetableBreak
        fields = [
            "name",
            "start_time",
            "end_time",
        ]

        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


BreakFormSet = inlineformset_factory(
    TimetableSetting,
    TimetableBreak,
    fields=[
        "name",
        "start_time",
        "end_time",
    ],
    extra=3,
    can_delete=True
)

SubjectConfigFormSet = inlineformset_factory(
    TimetableSetting,
    SubjectConfiguration,
    fields=[
        "subject",
        "teacher_assignment",
        "lessons_per_week",
        "is_fixed",
        "fixed_day",
        "fixed_start_time",
    ],
    extra=5,
    can_delete=True
)
