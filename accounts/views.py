from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages

def school_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            messages.success(request, f"Welcome, {user.username}!")

            # Redirect based on role
            if user.is_superuser or user.groups.filter(name="Admins").exists():
                return redirect("/admin_dashboard/")

            if user.groups.filter(name="Teacher").exists():
                return redirect("/teacher_dashboard/")

            if user.groups.filter(name="Parent").exists():
                return redirect("/parent_dashboard/")

            if user.groups.filter(name="PayrollManager").exists():
                return redirect("/payroll/")

            return redirect("/")  # fallback

        else:
            # Invalid credentials
            messages.error(request, "Invalid username or password. Please try again.")
            return redirect("login")  # reload login modal

    return redirect("/")
