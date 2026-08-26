from django import forms
from django.forms import ModelForm
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
import string
import logging
import json

from academics.models import Subject
from students.models import ClassGrade, Section, Student
from profiles.models import TeacherProfile

logger = logging.getLogger(__name__)
User = get_user_model()


# ================================
# ADD TEACHER FORM
# ================================

class AddUserForm(ModelForm):
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={"class": "subjects-checkbox"}),
        required=False,
    )

    # Blank = signal auto-generates; filled = manual override
    employee_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. EMP-001"}),
    )

    # JS sends "auto" or "manual" per row via hidden input
    emp_number_mode = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    # JS sends "true" if the class-teacher checkbox is ticked
    is_class_teacher = forms.BooleanField(required=False)

    # JSON list of Classroom PKs e.g. "[1,3,5]" — populated by the modal
    class_teacher_classrooms = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone"]
        widgets = {
            "username":   forms.TextInput(attrs={"placeholder": "e.g. jdoe"}),
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name":  forms.TextInput(attrs={"placeholder": "Last name"}),
            "email":      forms.EmailInput(attrs={"placeholder": "email@school.com"}),
            "phone":      forms.TextInput(attrs={"placeholder": "Phone"}),
        }

    def __init__(self, *args, **kwargs):
        self.role   = kwargs.pop("role", None)
        self.school = kwargs.pop("school", None)
        super().__init__(*args, **kwargs)
        self.fields["username"].required = False

        if self.role == "teacher" and self.school:
            self.fields["subjects"].queryset = Subject.objects.filter(school=self.school)
        else:
            for f in ["subjects", "employee_number", "emp_number_mode",
                      "is_class_teacher", "class_teacher_classrooms"]:
                self.fields[f].widget = forms.HiddenInput()

    def clean(self):
        cleaned_data = super().clean()
        has_data = any(cleaned_data.get(f) for f in
                       ["first_name", "last_name", "email", "phone"])

        if has_data and not cleaned_data.get("username"):
            self.add_error("username", "Username is required.")

        mode   = (cleaned_data.get("emp_number_mode") or "auto").strip()
        emp_no = (cleaned_data.get("employee_number") or "").strip()

        if self.role == "teacher" and mode == "manual" and has_data:
            if not emp_no:
                self.add_error("employee_number", "Employee number required (manual mode).")
            elif TeacherProfile.objects.filter(employee_number=emp_no).exists():
                self.add_error("employee_number", f'"{emp_no}" is already taken.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role   = self.role
        user.school = self.school
        if not user.school:
            raise ValueError("School must be provided.")

        password = get_random_string(10, string.ascii_letters + string.digits)
        user.set_password(password)
        user.must_change_password = True

        if commit:
            user.save()

            if user.role == "teacher":
                try:
                    tp = user.teacher_profile
                    tp.school = user.school

                    mode   = (self.cleaned_data.get("emp_number_mode") or "auto").strip()
                    emp_no = (self.cleaned_data.get("employee_number") or "").strip()
                    if mode == "manual" and emp_no:
                        tp.employee_number = emp_no

                    is_ct = bool(self.cleaned_data.get("is_class_teacher"))
                    tp.is_class_teacher = is_ct
                    tp.save()
                    tp.subjects.set(self.cleaned_data.get("subjects", []))

                    if is_ct:
                        raw = (self.cleaned_data.get("class_teacher_classrooms") or "").strip()
                        if raw:
                            try:
                                ids = json.loads(raw)
                                from students.models import Classroom
                                Classroom.objects.filter(
                                    pk__in=ids,
                                    class_grade__school=user.school,
                                ).update(class_teacher=user)
                            except Exception as e:
                                logger.error("Classroom assign failed for %s: %s", user.pk, e)

                except Exception as e:
                    logger.error("TeacherProfile update failed for %s: %s", user.pk, e)

            if user.email:
                send_mail(
                    subject="Your Account Has Been Created",
                    message=(
                        f"Hello {user.first_name},\n\n"
                        f"Username: {user.username}\nPassword: {password}\n\n"
                        f"You must change your password after first login.\n\nSchool Admin"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

        user.generated_password = password
        return user


# ================================
# ADD STUDENT FORM
# ================================

class AddStudentForm(ModelForm):
    GENDER_CHOICES   = [("", "Gender"), ("male", "Male"), ("female", "Female")]
    BOARDING_CHOICES = [("", "Boarder?"), ("yes", "Boarder"), ("no", "Day Scholar")]

    admission_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "e.g. ADM-001"}),
    )
    gender     = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    is_boarder = forms.ChoiceField(choices=BOARDING_CHOICES, required=False)

    current_class = forms.ModelChoiceField(
        queryset=ClassGrade.objects.none(), required=False, empty_label="Select grade",
    )
    current_section = forms.ModelMultipleChoiceField(
        queryset=Section.objects.none(), required=False,
        widget=forms.CheckboxSelectMultiple(attrs={"class": "section-checkbox"}),
    )

    class Meta:
        model  = User
        fields = ["username", "first_name", "last_name", "email", "phone"]
        widgets = {
            "username":   forms.HiddenInput(),
            "first_name": forms.TextInput(attrs={"placeholder": "First name"}),
            "last_name":  forms.TextInput(attrs={"placeholder": "Last name"}),
            "email":      forms.EmailInput(attrs={"placeholder": "Email"}),
            "phone":      forms.TextInput(attrs={"placeholder": "Phone"}),
        }

    def __init__(self, *args, **kwargs):
        self.role   = kwargs.pop("role", None)
        self.school = kwargs.pop("school", None)
        super().__init__(*args, **kwargs)
        self.fields["username"].required = False
        if self.school:
            self.fields["current_class"].queryset   = ClassGrade.objects.filter(school=self.school)
            self.fields["current_section"].queryset = Section.objects.filter(school=self.school)

    def clean(self):
        cleaned_data = super().clean()
        adm_no = (cleaned_data.get("admission_number") or "").strip()
        has_data = adm_no or any(
            cleaned_data.get(f) for f in
            ["first_name", "last_name", "email", "phone",
             "gender", "is_boarder", "current_class", "current_section"]
        )
        if not has_data:
            return cleaned_data

        if not adm_no:
            self.add_error("admission_number", "Admission number is required.")
        else:
            from profiles.models import StudentProfile
            if StudentProfile.objects.filter(admission_number=adm_no).exists():
                self.add_error("admission_number", f'"{adm_no}" is already taken.')
            else:
                cleaned_data["username"] = adm_no

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role   = "student"
        user.school = self.school
        if not user.school:
            raise ValueError("School must be provided.")

        adm_no   = (self.cleaned_data.get("admission_number") or "").strip()
        password = get_random_string(10, string.ascii_letters + string.digits)
        user.set_password(password)
        user.must_change_password = True

        if commit:
            user.save()
            sections = self.cleaned_data.get("current_section")

            student, _ = Student.objects.update_or_create(
                user=user,
                defaults={
                    "school": self.school,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "gender": self.cleaned_data.get("gender", ""),
                    "is_boarder": self.cleaned_data.get("is_boarder", "no"),
                    "current_class": self.cleaned_data.get("current_class"),
                    "admission_no": adm_no,
                }
            )

            student.current_section.set(sections or [])

            try:
                from profiles.models import StudentProfile

                current_class = self.cleaned_data.get("current_class")
                sections = self.cleaned_data.get("current_section")
                chosen_section = sections.first() if sections else None

                if current_class and chosen_section:
                     classroom = f"{current_class} - {chosen_section}"
                elif current_class:
                    classroom = str(current_class)
                else:
                    classroom = ""

                StudentProfile.objects.update_or_create(
                    user=user,
                    defaults={
                    "admission_number": adm_no,
                    "classroom": classroom,
                     }
                    )

            except Exception as e:
                    logger.error(
                    "StudentProfile update failed for %s: %s",
                    user.pk,e)
                            
                             
            if user.email:
                send_mail(
                    subject="Your Student Account Has Been Created",
                    message=(
                        f"Hello {user.first_name},\n\n"
                        f"Admission No: {adm_no}\nPassword: {password}\n\n"
                        f"Please change your password after first login.\n\nSchool Admin"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )

        user.generated_password = password
        return user


# ================================
# ADMIN USER CREATION
# ================================

class AdminCreateUserForm(forms.ModelForm):
    class Meta:
        model   = User
        fields  = ["username", "email", "first_name", "last_name", "password", "role"]
        widgets = {"password": forms.PasswordInput()}

    def save(self, commit=True, school=None):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if school:
            user.school = school
        if commit:
            user.save()
        return user


# ================================
# SCHOOL ADMIN CREATION
# ================================

class SchoolAdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model  = User
        fields = ["username", "email", "password", "school"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role     = "admin"
        user.is_staff = True
        if commit:
            user.save()
        return user
