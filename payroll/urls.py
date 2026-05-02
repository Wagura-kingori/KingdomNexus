from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    path('employees/', views.employees_list, name='employees'),
    path('employees/add/', views.employee_form, name='employee_add'),
    path('employees/<int:pk>/edit/', views.employee_form, name='employee_edit'),

    path('components/', views.components_list, name='components'),

    path('periods/', views.payroll_periods, name='periods'),
    path('periods/add/', views.payroll_period_form, name='period_add'),
    path('periods/<int:pk>/edit/', views.payroll_period_form, name='period_edit'),

    path('process/<int:period_id>/', views.process_payroll, name='process_payroll'),

    path('payslips/', views.payslips_list, name='payslips_all'),
    path('payslips/period/<int:period_id>/', views.payslips_list, name='payslips_list'),
    path('payslip/<int:pk>/', views.payslip_detail, name='payslip_detail'),
    # path('payslip/<int:payslip_id>/payment/', views.record_payment, name='record_payment'),
    path('payslip/<int:pk>/pdf/', views.payslip_pdf, name='payslip_pdf'),

]
