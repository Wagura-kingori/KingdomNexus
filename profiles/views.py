from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TeacherProfile, ParentProfile, PayrollProfile
from .forms import TeacherProfileForm, ParentProfileForm, PayrollProfileForm


@login_required
def profile_view(request):
    
   # Route each role to the correct profile view.

    role = request.user.role

    if role == "teacher":
        return teacher_profile(request)
    elif role == "parent":
        return parent_profile(request)
    elif role == "payroll":
        return payroll_profile(request)
    else:
        # admin / superadmin — no profile form needed
        return render(request, "profiles/profile_base.html", {
            "user": request.user
        })


@login_required
def teacher_profile(request):
    profile, _ = TeacherProfile.objects.get_or_create(
        user=request.user,
        defaults={
            "school": request.user.school,
            "employee_number": request.user.username.upper()[:8],
        }
    )

    form = TeacherProfileForm(
        request.POST or None,
        instance=profile
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profiles:view")

    return render(request, "profiles/teacher_profile.html", {
        "form": form,
        "profile": profile,
    })


@login_required
def parent_profile(request):
    profile, _ = ParentProfile.objects.get_or_create(user=request.user)

    form = ParentProfileForm(
        request.POST or None,
        instance=profile
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profiles:view")

    return render(request, "profiles/parent_profile.html", {
        "form": form,
        "profile": profile,
    })


@login_required
def payroll_profile(request):
    profile, _ = PayrollProfile.objects.get_or_create(
        user=request.user,
        defaults={"school": request.user.school}
    )

    form = PayrollProfileForm(
        request.POST or None,
        instance=profile
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profiles:view")

    return render(request, "profiles/payroll_profile.html", {
        "form": form,
        "profile": profile,
    })