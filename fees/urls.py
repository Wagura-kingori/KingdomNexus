from django.urls import path
from . import views
app_name = "fees" 

urlpatterns = [
    path('structures/', views.fee_structure_list, name='fee_structure_list'),
    path('structures/add/', views.fee_structure_form, name='fee_structure_form'),

    path('student-fees/', views.student_fees_list, name='student_fees_list'),
    path('student-fees/add/', views.student_fee_form, name='student_fee_form'),

    path('payments/', views.payment_list, name='payment_list'),
    path('payments/add/', views.payment_form, name='payment_form'),
]
