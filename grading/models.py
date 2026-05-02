from django.db import models

class GradeRange(models.Model):
    min_score = models.IntegerField()
    max_score = models.IntegerField()
    grade = models.CharField(max_length=2)
    remark = models.CharField(max_length=100)

    class Meta:
        ordering = ['-min_score']  # highest scores first

    def __str__(self):
        return f"{self.grade} ({self.min_score}-{self.max_score})"
def calculate_grade(score):
    grade_range = GradeRange.objects.filter(
        min_score__lte=score,
        max_score__gte=score
    ).first()

    if grade_range:
        return grade_range.grade, grade_range.remark
    return "N/A", "Not Defined"
