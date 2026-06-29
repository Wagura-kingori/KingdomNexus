from django.urls import path
from . import views
from .views import manage_subjects
from .views import SubjectListAPIView
app_name = "academics" 
urlpatterns = [
    path('subjects/', SubjectListAPIView.as_view(), name='subject-list'),
    # SUBJECTS
    path('subjects/', views.subjects_list, name='subjects_list'),
    path("schools/<int:school_id>/subjects/", manage_subjects, name="manage_subjects"),
    path('subjects/edit/<int:pk>/', views.subject_edit, name='subject_edit'),

    # ENROLLMENTS
    path('enrollments/', views.enrollments_list, name='enrollments_list'),
    path('enrollments/add/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/edit/<int:pk>/', views.enrollment_edit, name='enrollment_edit'),
]
