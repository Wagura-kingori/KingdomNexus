from django import forms
from .models import Route, Vehicle, StudentTransportAssignment, TransportPayment
from students.models import ClassGrade


class RouteForm(forms.ModelForm):
    class Meta:
        model = Route
        fields = ['name', 'pickup_points', 'fee']
        widgets = {
            'pickup_points': forms.Textarea(attrs={'rows': 3}),
        }


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['name', 'registration_no', 'capacity', 'driver', 'route']


class TransportAssignmentForm(forms.ModelForm):
    class Meta:
        model = StudentTransportAssignment
        fields = ['student', 'route', 'vehicle']


class TransportPaymentForm(forms.ModelForm):
    class Meta:
        model = TransportPayment
        fields = ['assignment', 'amount', 'date', 'method', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
