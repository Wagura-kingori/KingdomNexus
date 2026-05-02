from django.db import models
from students.models import Student
from django.utils import timezone
from datetime import timedelta
from schools.models import School
school = models.ForeignKey(School, on_delete=models.CASCADE)

class BookCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True)
    isbn = models.CharField(max_length=30, blank=True)
    copies_total = models.PositiveIntegerField(default=1)
    copies_available = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.title} ({self.author})"


def default_due_date():
    return timezone.now().date() + timedelta(days=14)

class BorrowRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date_borrowed = models.DateField(default=timezone.now)
    due_date = models.DateField(default=default_due_date)
    date_returned = models.DateField(null=True, blank=True)

    @property
    def is_overdue(self):
        return not self.date_returned and timezone.now().date() > self.due_date

    def __str__(self):
        return f"{self.student} → {self.book}"