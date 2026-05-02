from django.urls import path
from . import views
from .views import RoleBasedLoginView



app_name = "users"
urlpatterns = [
    # path('login/', views.login_view, name='login'),
    path("login/", RoleBasedLoginView.as_view(), name="login"),
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path('force-password-change/', views.force_password_change, name='force_password_change'),
    path('users/<int:user_id>/delete/', views.user_delete_ajax, name='user_delete_ajax'),
    path('users/<int:user_id>/update/', views.user_update_ajax, name='user_update_ajax'),
    # path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('payroll_manager_dashboard/', views. payroll_manager_dashboard, name='payroll_manager_dashboard'),
    path('parent_dashboard/', views.parent_dashboard, name='parent_dashboard'),
    path(
    "setup/admin/add/",
    views.add_school_admin,
    name="add_school_admin"),
    path("add/<int:school_id>/<str:role>/", views.add_user, name="add_user"),
    path('users/<int:user_id>/class-teacher/', views.user_class_teacher_ajax, name='user_class_teacher_ajax'),


    # path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
]
