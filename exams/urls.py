from django.urls import path
from . import views

app_name = "exams"

urlpatterns = [
    # Exam Types
    path("types/", views.exam_types_list, name="exam_types_list"),
    path("types/add/", views.exam_type_create, name="exam_type_create"),
    path("types/<int:id>/edit/", views.exam_types_form, name="exam_types_form"),

    # Exams
    path("", views.exams_list, name="exams_list"),
    path("add/", views.exam_create, name="exam_create"),
    path("<int:id>/edit/", views.exams_form, name="exams_form"),

    # Results
    path("results/", views.results_list, name="results_list"),
    path("results/<int:id>/edit/", views.results_form, name="results_form"),
    path("results/student/<int:student_id>/", views.student_results, name="student_results"),
    path("<int:exam_id>/ranking/", views.class_ranking, name="class_ranking"),
]