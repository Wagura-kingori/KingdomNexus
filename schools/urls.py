from django.urls import path
from .views import setup_dashboard, add_school, school_dashboard

app_name = "schools"

urlpatterns = [
    path("setup/", setup_dashboard, name="setup_dashboard"),
    path("setup/schools/add/", add_school, name="add_school"),
    path("<int:pk>/dashboard/", school_dashboard, name="school_dashboard"),
]
