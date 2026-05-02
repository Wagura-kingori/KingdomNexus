from django.urls import path
from . import views

app_name = "timetable"

urlpatterns = [
    path("class/<int:classroom_id>/setup/", views.setup_timetable, name="setup"),
    path("class/<int:classroom_id>/generate/", views.generate_timetable, name="generate"),
    path("class/<int:classroom_id>/view/", views.view_timetable, name="view"),
    path("teacher/workload/", views.teacher_workload, name="teacher_workload"),
    path(
    "",
    views.timetable_list,
    name="timetable_list"
),
]