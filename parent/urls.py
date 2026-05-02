from django.urls import path
from . import views

app_name = "parent" 

urlpatterns = [
    path("", views.parent_dashboard, name="dashboard"),
    # path("profile/", views.parent_profile, name="profile"),
    path("children/", views.parent_children, name="children_list"),
    path("children/<int:child_id>/", views.parent_child_detail, name="child_detail"),
    path("children/<int:child_id>/results/", views.parent_child_results, name="child_results"),
    path("children/<int:child_id>/attendance/", views.parent_child_attendance, name="child_attendance"),
    path("children/<int:child_id>/fees/", views.parent_child_fees, name="child_fees"),
    path("notifications/", views.parent_notifications, name="notifications"),
]
