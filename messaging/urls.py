from django.urls import path
from . import views

app_name = "messaging"   

urlpatterns = [
    path('notices/', views.notices_list, name='notices_list'),
    path('notices/new/', views.notice_create, name='notice_create'),

    path('messages/', views.messages_list, name='messages_list'),
    path('messages/new/', views.send_message, name='send_message'),
]