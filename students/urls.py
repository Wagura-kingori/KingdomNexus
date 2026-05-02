from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='student_list'),
    path('add/', views.add_student, name='add_student'),
    path('edit/<int:student_id>/', views.edit_student, name='edit_student'),
    # Main management page
    path(
        "schools/<int:school_id>/grades/",
        views.manage_grades,
        name="manage_grades",
    ),

    # Grade CRUD (AJAX)
    path("grades/create/<int:school_id>/",  views.grade_create,  name="grade_create"),
    path("grades/<int:grade_id>/update/",   views.grade_update,  name="grade_update"),
    path("grades/<int:grade_id>/delete/",   views.grade_delete,  name="grade_delete"),

    # Section CRUD (AJAX)
    path("sections/create/<int:grade_id>/", views.section_create, name="section_create"),
    path("sections/<int:section_id>/update/", views.section_update, name="section_update"),
    path("sections/<int:section_id>/delete/", views.section_delete, name="section_delete"),
]
