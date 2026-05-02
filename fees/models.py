from django.db import models
from students.models import Student
from academics.models import Classroom
from django.utils import timezone
from schools.models import School
school = models.ForeignKey(School, on_delete=models.CASCADE)

# ---------------------------------------------
# NEW MODEL
# ---------------------------------------------
class Fee(models.Model):
    name = models.CharField(max_length=100)  # e.g. Tuition, Lunch, Bus, Development
    description = models.TextField(blank=True)
    default_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name


# ---------------------------------------------
# Fee structure per class & term
# ---------------------------------------------
class FeeStructure(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    term = models.CharField(max_length=50)  # e.g. Term 1, Term 2

    
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    fee_items = models.ManyToManyField(Fee, through="FeeStructureItem")

    def __str__(self):
        return f"{self.classroom.name} - {self.term} - {self.amount}"


# Linking table to attach Fee + Amount to FeeStructure
class FeeStructureItem(models.Model):
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.fee_structure} → {self.fee.name}: {self.amount}"


# ---------------------------------------------
# Invoices
# ---------------------------------------------
class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.student.full_name} - {self.amount}"


# ---------------------------------------------
# Studens Fees
# ---------------------------------------------
class StudentFee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2)

    def update_balance(self):
        self.balance = self.total_amount - self.amount_paid

    def __str__(self):
        return f"{self.student.full_name} - {self.fee_structure.term}"


# ---------------------------------------------
# Payments
# ---------------------------------------------
class Payment(models.Model):
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    method = models.CharField(max_length=50, default="Cash")  # Cash, MPesa, Bank

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update parent table
        fee = self.student_fee
        fee.amount_paid += self.amount
        fee.update_balance()
        fee.save()

    def __str__(self):
        return f"{self.student_fee.student.full_name} - {self.amount} on {self.date}"
