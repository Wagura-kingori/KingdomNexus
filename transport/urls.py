from django.urls import path
from . import views

app_name = 'transport'

urlpatterns = [
    # routes
    path('routes/', views.routes_list, name='routes'),
    path('routes/add/', views.route_create, name='route_create'),
    path('routes/<int:pk>/edit/', views.route_edit, name='route_edit'),

    # vehicles
    path('vehicles/', views.vehicles_list, name='vehicles'),
    path('vehicles/add/', views.vehicle_create, name='vehicle_create'),
    path('vehicles/<int:pk>/edit/', views.vehicle_edit, name='vehicle_edit'),

    # assignments
    path('assignments/', views.assignments_view, name='assignments'),

    # fees & payments
    path('fees/', views.transport_fees_view, name='transport_fees'),
    path('payments/', views.payments_list, name='payments'),
    path('payments/add/', views.payment_create, name='payment_create'),
]
