from django.contrib import admin
from .models import Route, Vehicle, StudentTransportAssignment, TransportPayment

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('name', 'fee')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'registration_no', 'capacity', 'route', 'driver')

@admin.register(StudentTransportAssignment)
class StudentTransportAssignmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'route', 'vehicle', 'assigned_on')

@admin.register(TransportPayment)
class TransportPaymentAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'amount', 'date', 'method')
