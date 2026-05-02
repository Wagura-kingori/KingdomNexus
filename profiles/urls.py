from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("", views.profile_view, name="view"),
    path("teacher/", views.teacher_profile, name="teacher"),
    path("parent/", views.parent_profile, name="parent"),
    path("payroll/", views.payroll_profile, name="payroll"),
]