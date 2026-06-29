from django.db import models
from django.conf import settings
from students.models import Student, ClassGrade
from django.utils import timezone

User = settings.AUTH_USER_MODEL


class Route(models.Model):
    name = models.CharField(max_length=200)
    pickup_points = models.TextField(blank=True)  
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.name} (KES {self.fee})"


class Vehicle(models.Model):
    name = models.CharField(max_length=200)
    registration_no = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(default=20)
    driver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicles")
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name="vehicles")

    def __str__(self):
        return f"{self.name} - {self.registration_no}"


class StudentTransportAssignment(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='transport_assignment')
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    assigned_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} -> {self.route}"


class TransportPayment(models.Model):
    assignment = models.ForeignKey(StudentTransportAssignment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    method = models.CharField(max_length=50, default="Cash")
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.assignment.student} - KES {self.amount} on {self.date}"
