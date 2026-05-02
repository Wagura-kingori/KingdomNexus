from django.urls import path
from . import views
app_name = "hostell" 

urlpatterns = [
    path("hostels/", views.hostel_list, name="hostel_list"),
    path("hostels/add/", views.hostel_form, name="hostel_add"),
    path("hostels/<int:pk>/edit/", views.hostel_form, name="hostel_edit"),

    path("rooms/", views.room_list, name="room_list"),
    path("rooms/add/", views.room_form, name="room_add"),
    path("rooms/<int:pk>/edit/", views.room_form, name="room_edit"),

    path("boarders/", views.boarder_list, name="boarder_list"),
    path("boarders/add/", views.boarder_form, name="boarder_add"),
    path("boarders/<int:pk>/edit/", views.boarder_form, name="boarder_edit"),
]
