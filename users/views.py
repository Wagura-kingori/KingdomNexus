from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.forms import modelformset_factory
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from schools.models import School
from students.models import ClassGrade, Section, Classroom
from .models import User
from .serializers import UserSerializer
from .forms import AddUserForm, AddStudentForm, SchoolAdminForm
from .decorators import role_required, super_admin_required
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response



# -----------------------------
# ADD USERS (FORMSET)
# -----------------------------
@login_required
def add_user(request, school_id, role):
    school = get_object_or_404(School, id=school_id)

    if not request.user.is_superadmin() and request.user.school != school:
        messages.error(request, "You are not allowed to add users to this school.")
        return redirect("home")

    users_qs = User.objects.filter(school=school, role=role).order_by("-id")

    if role == "teacher":
        users_qs = users_qs.prefetch_related("teacher_profile__subjects")
    elif role == "student":
        users_qs = users_qs.prefetch_related(
            "student_account__current_class",
            "student_account__current_section",
        )

    users = users_qs

    # Choose the correct form class
    FormClass = AddStudentForm if role == "student" else AddUserForm

    UserFormSet = modelformset_factory(
        User,
        form=FormClass,
        extra=2,
        can_delete=False,
    )

    # Extra context for the student template (grade/section JSON)
    extra_ctx = {}
    if role == "student":
        grades_list = list(
            ClassGrade.objects.filter(school=school).values("id", "name")
        )
        # Build sections keyed by grade id for the JS dynamic filter
        sections_by_grade = {}
        for sec in Section.objects.filter(school=school).select_related("class_grade"):
            gid = str(sec.class_grade_id)
            sections_by_grade.setdefault(gid, []).append(
                {"id": sec.id, "name": sec.name}
            )
        # Serialize to JSON strings 
        extra_ctx["grades_json"]           = json.dumps(grades_list)
        extra_ctx["sections_by_grade_json"] = json.dumps(sections_by_grade)

    # For teacher role — build classroom list from grades+sections.
    # section_id is NOT NULL in the DB so we only create Classroom rows
    # for grade+section pairs — grades with no sections are skipped.
    if role == "teacher":
        existing_cls = {
            (c.class_grade_id, c.section_id): c
            for c in Classroom.objects.filter(
                class_grade__school=school
            ).select_related("class_grade", "section", "class_teacher")
        }
        classrooms_list = []
        for grade in (
            ClassGrade.objects
            .filter(school=school)
            .prefetch_related("sections")
            .order_by("name")
        ):
            for section in grade.sections.all().order_by("name"):
                key = (grade.pk, section.pk)
                if key not in existing_cls:
                    # Auto-create the Classroom row so it can be assigned
                    obj, _ = Classroom.objects.get_or_create(
                        class_grade=grade,
                        section=section,
                        defaults={"class_teacher": None},
                    )
                    existing_cls[key] = obj
                c = existing_cls[key]
                classrooms_list.append({
                    "id":         c.pk,
                    "grade":      grade.name,
                    "section":    section.name,
                    "label":      f"{grade.name} \u2014 {section.name}",
                    "teacher_id": c.class_teacher_id,
                })
        extra_ctx["classrooms_json"] = json.dumps(classrooms_list)

    if request.method == "POST":
        formset = UserFormSet(
            request.POST,
            queryset=User.objects.none(),
            form_kwargs={"role": role, "school": school},
        )

        if formset.is_valid():
            created = 0
            for form in formset:
                if not form.cleaned_data:
                    continue
                has_data = any(
                    form.cleaned_data.get(f)
                    for f in ["username", "first_name", "last_name", "email", "phone"]
                )
                if not has_data:
                    continue
              
                if form.errors:
                    continue
                # Never save without a username
                if not form.cleaned_data.get('username'):
                    continue
                form.save()
                created += 1

            if created:
                messages.success(request, f"{created} {role}(s) created successfully.")
            else:
                messages.warning(request, "No users were added.")
            return redirect(request.path)

    else:
        formset = UserFormSet(
            queryset=User.objects.none(),
            form_kwargs={"role": role, "school": school},
        )

    return render(request, "users/add_user.html", {
        "school":  school,
        "role":    role,
        "users":   users,
        "formset": formset,
        **extra_ctx,
    })


# -----------------------------
# AJAX UPDATE USER
# -----------------------------
@login_required
@require_POST
def user_update_ajax(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if not request.user.is_superadmin() and request.user.school != user.school:
        return JsonResponse({"success": False}, status=403)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False}, status=400)

    user.first_name = data.get("first_name", user.first_name).strip()
    user.last_name  = data.get("last_name",  user.last_name).strip()
    user.email      = data.get("email",      user.email).strip()
    user.phone      = data.get("phone",      user.phone or "").strip()
    user.save()

    # Update teacher subjects if provided
    if user.role == "teacher" and "subject_ids" in data:
        try:
            from academics.models import Subject
            from profiles.models import TeacherProfile
            tp = user.teacher_profile
            subject_ids = [int(i) for i in data["subject_ids"] if str(i).isdigit()]
            subjects = Subject.objects.filter(
                pk__in=subject_ids,
                school=user.school,
            )
            tp.subjects.set(subjects)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(
                "Subject update failed for user %s: %s", user.pk, e
            )
            return JsonResponse({"success": False, "error": "Subjects could not be saved."})

    return JsonResponse({"success": True})


# -----------------------------
# AJAX DELETE USER
# -----------------------------
@login_required
@require_POST
def user_delete_ajax(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        return JsonResponse({"success": False})
    name = f"{user.first_name} {user.last_name}".strip() or user.username
    user.delete()
    return JsonResponse({"success": True, "name": name})


# -----------------------------
# ADD SCHOOL ADMIN
# -----------------------------
@login_required
@super_admin_required
def add_school_admin(request):
    form = SchoolAdminForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("schools:setup_dashboard")
    return render(request, "users/add_school_admin.html", {"form": form})


# -----------------------------
# AJAX CLASS TEACHER ASSIGN
# -----------------------------
@login_required
@require_POST
def user_class_teacher_ajax(request, user_id):
    """Save classroom assignments for an existing teacher from the Manage tab."""
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_superadmin() and request.user.school != user.school:
        return JsonResponse({"success": False, "error": "Access denied."}, status=403)

    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({"success": False, "error": "Invalid JSON."}, status=400)

    classroom_ids = data.get("classroom_ids", [])

    try:
        from students.models import Classroom
        # Clear previous assignments for this teacher
        Classroom.objects.filter(class_teacher=user).update(class_teacher=None)
        # Set new ones
        if classroom_ids:
            Classroom.objects.filter(
                pk__in=classroom_ids,
                class_grade__school=user.school,
            ).update(class_teacher=user)

        # Update TeacherProfile.is_class_teacher flag
        tp = user.teacher_profile
        tp.is_class_teacher = bool(classroom_ids)
        tp.save(update_fields=["is_class_teacher"])

        return JsonResponse({"success": True, "count": len(classroom_ids)})
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)})


# -----------------------------
# USER API
# -----------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset           = User.objects.all()
    serializer_class   = UserSerializer
    permission_classes = [IsAdminUser]




# -----------------------------
# AJAX: SAVE CLASS TEACHER ASSIGNMENTS
# -----------------------------
@login_required
@require_POST
def save_class_teacher(request, user_id):
    """
    Receives a list of classroom IDs and marks that teacher as
    class_teacher on each Classroom row. Clears previous assignments first.
    Also sets TeacherProfile.is_class_teacher accordingly.
    """
    user = get_object_or_404(User, id=user_id)
    if not request.user.is_superadmin() and request.user.school != user.school:
        return JsonResponse({"success": False, "error": "Access denied."}, status=403)

    try:
        data        = json.loads(request.body)
        classroom_ids = [int(x) for x in (data.get("classroom_ids") or [])]
    except (ValueError, TypeError):
        return JsonResponse({"success": False, "error": "Invalid data."}, status=400)

    # Clear all classrooms where this teacher is currently assigned
    Classroom.objects.filter(class_teacher=user).update(class_teacher=None)

    if classroom_ids:
        Classroom.objects.filter(id__in=classroom_ids).update(class_teacher=user)

    # Update is_class_teacher flag on profile
    try:
        tp = user.teacher_profile
        tp.is_class_teacher = bool(classroom_ids)
        tp.save(update_fields=["is_class_teacher"])
    except Exception:
        pass

    return JsonResponse({
        "success":       True,
        "is_class_teacher": bool(classroom_ids),
        "classroom_ids": classroom_ids,
    })

# -----------------------------
# LOGIN VIEW
# -----------------------------
class RoleBasedLoginView(LoginView):
    template_name = "users/login.html"

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self._role_url(request.user))
        return redirect("/")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        referer = self.request.META.get("HTTP_REFERER", "/")
        return redirect(referer)

    def get_success_url(self):
        return self._role_url(self.request.user)

    def _role_url(self, user):
        if user.must_change_password:
            return reverse("users:force_password_change")
        if user.role == "superadmin":
            return "/dashboard/super/"
        if not user.school:
            return "/no-school-assigned/"
        if user.role == "admin":
            return f"/schools/{user.school.id}/dashboard/"
        if user.role == "teacher":
            return reverse("teachers:dashboard")
        if user.role == "payroll":
            return f"/schools/{user.school.id}/payroll/dashboard/"
        if user.role == "parent":
            return "/parent/dashboard/"
        return "/"


# -----------------------------
# DASHBOARDS
# -----------------------------
@login_required
@role_required(allowed_roles=["admin"])
def admin_dashboard(request):
    return render(request, "dashboard/admin_dashboard.html")


@login_required
@role_required(allowed_roles=["teacher"])
def teacher_dashboard(request):
    return render(request, "dashboard/teacher_dashboard.html")


@login_required
@role_required(allowed_roles=["parent"])
def parent_dashboard(request):
    return render(request, "dashboard/parent_dashboard.html")


@login_required
@role_required(allowed_roles=["payroll"])
def payroll_manager_dashboard(request):
    return render(request, "payroll/payroll_dashboard.html")


# -----------------------------
# FORCE PASSWORD CHANGE
# -----------------------------
@login_required
@login_required
def force_password_change(request):
    if not request.user.must_change_password:
        return redirect("home")

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            user.must_change_password = False
            user.save()
            messages.success(request, "Password changed successfully.")
            return redirect("home")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, "users/force_password_change.html", {"form": form})




@api_view(['GET'])
@authentication_classes([SessionAuthentication])
@permission_classes([AllowAny])
def current_user_api(request):
    if not request.user.is_authenticated:
        return Response({'authenticated': False})

    user = request.user
    data = {
        'authenticated': True,
        'id': user.id,
        'name': user.get_full_name() or user.username,
        'role': user.role,
        'is_admin': user.role in ('admin', 'superadmin') or user.is_superuser,
        'is_superadmin': user.role == 'superadmin' or user.is_superuser,
        'school': None,
        'classroom': None,
    }

    if user.school:
        data['school'] = {
            'id': user.school.id,
            'name': user.school.name,
        }

    classroom = Classroom.objects.filter(
        class_teacher=user
    ).select_related('class_grade', 'section').first()

    if classroom:
        data['classroom'] = {
            'id': classroom.id,
            'name': str(classroom),
            'class_grade': classroom.class_grade.name,
            'section': classroom.section.name,
        }

    return Response(data)