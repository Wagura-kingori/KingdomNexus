from django.urls import path
from . import views

app_name = "teachers"

urlpatterns = [
    path("dashboard/",
         views.teacher_dashboard, name="dashboard"),

    # Subject teacher routes — scoped to assignment
    path("assignment/<int:assignment_id>/students/",
         views.teacher_subject_students, name="subject_students"),
    path("assignment/<int:assignment_id>/exams/",
         views.teacher_subject_results, name="subject_exams"),
    path("assignment/<int:assignment_id>/exam/<int:exam_id>/enter/",
         views.teacher_enter_results, name="enter_results"),
    path("assignment/<int:assignment_id>/exam/create/",
         views.teacher_create_exam, name="create_exam"),

    # Class teacher routes
    path("classroom/<int:classroom_id>/",
         views.class_teacher_classroom, name="class_teacher_view"),
    path("classroom/<int:classroom_id>/assign/",
         views.assign_subject, name="assign_subject"),
]