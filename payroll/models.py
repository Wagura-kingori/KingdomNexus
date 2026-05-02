from django.db import models
from django.conf import settings
from django.utils import timezone
from schools.models import School

User = settings.AUTH_USER_MODEL


class Employee(models.Model):
    """
    Represents any paid employee (teacher, admin staff, support staff).
    Employees belong to ONE school.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="employees"
    )

    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    staff_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    date_joined = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.staff_id})"


class SalaryComponent(models.Model):
    """
    Earnings or deductions.
    Components are GLOBAL (reusable across schools).
    """

    KIND_CHOICES = (
        ('earning', 'Earning'),
        ('deduction', 'Deduction'),
    )

    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    default_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    def __str__(self):
        return f"{self.name} ({self.kind})"


class PayrollPeriod(models.Model):
    """
    Payroll periods are SCHOOL-specific.
    Example: March 2025 – School A
    """

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="payroll_periods"
    )

    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    processed = models.BooleanField(default=False)
    processed_on = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('school', 'start_date', 'end_date')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.school.name})"


class Payslip(models.Model):
    """
    Payslip for a single employee in a payroll period.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="payslips"
    )

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='payslips'
    )

    period = models.ForeignKey(
        PayrollPeriod,
        on_delete=models.CASCADE,
        related_name='payslips'
    )

    gross = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    created_on = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'period')
        ordering = ['-created_on']

    def __str__(self):
        return f"Payslip: {self.employee.name} - {self.period.name}"


class PayslipLine(models.Model):
    """
    Individual earnings or deductions on a payslip.
    """

    payslip = models.ForeignKey(
        Payslip,
        on_delete=models.CASCADE,
        related_name='lines'
    )

    component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    is_deduction = models.BooleanField(default=False)

    def __str__(self):
        t = "Deduction" if self.is_deduction else "Earning"
        name = self.component.name if self.component else "Custom"
        return f"{t}: {name} - {self.amount}"


class Payment(models.Model):
    """
    Record of actual payment for a payslip.
    """

    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    payslip = models.ForeignKey(
        Payslip,
        on_delete=models.CASCADE,
        related_name='payments'
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=50, default="Bank")
    reference = models.CharField(max_length=200, blank=True)
    paid_on = models.DateField(default=timezone.now)

    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Payment {self.amount} for {self.payslip}"


class EmployeeComponent(models.Model):
    """
    Custom salary components for an employee.
    Example: extra allowance or special deduction.
    """

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="custom_components"
    )

    component = models.ForeignKey(
        SalaryComponent,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('employee', 'component')

    def __str__(self):
        return f"{self.employee} - {self.component} ({self.amount})"
