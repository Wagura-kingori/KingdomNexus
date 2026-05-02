from django.urls import path
from . import views

app_name = "attendance" 

urlpatterns = [
    path('', views.attendance_list, name='attendance_list'),
    path('take/<int:class_id>/', views.attendance_take, name='attendance_take'),
]