from django.db import models
from students.models import Student
from grading.models import calculate_grade
from .utils import calculate_class_ranking
from schools.models import School


class ExamType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Exam(models.Model):
    name = models.CharField(max_length=200)
    term = models.CharField(max_length=20)
    year = models.IntegerField()
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, null=True)
    date = models.DateField(null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.term} {self.year}"


class ExamResult(models.Model):
    exam    = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(           
        "academics.Subject",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="exam_results"
    )
    score   = models.FloatField()
    grade   = models.CharField(max_length=5, blank=True)
    remark  = models.CharField(max_length=100, blank=True)
    total_score   = models.FloatField(default=0)
    average_score = models.FloatField(default=0)
    position      = models.IntegerField(default=0)

    class Meta:
        unique_together = ("exam", "student", "subject") 

    def save(self, *args, **kwargs):
        if self.score is not None:
            self.grade, self.remark = calculate_grade(self.score)
        super().save(*args, **kwargs)
        calculate_class_ranking(
            exam=self.exam,
            classroom=self.student.current_class
        )

    @staticmethod
    def get_student_results(student, exam):
        return ExamResult.objects.filter(student=student, exam=exam)

    def __str__(self):
        return f"{self.student} - {self.exam} ({self.score})"