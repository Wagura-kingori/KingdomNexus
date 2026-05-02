from django.db import models


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True)
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="subjects"
    )

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    class_grade = models.ForeignKey(
        "students.ClassGrade",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    section = models.ForeignKey(
        "students.Section",
        on_delete=models.CASCADE,
        related_name="enrollments"
    )
    subjects = models.ManyToManyField(
        Subject,
        blank=True,
        related_name="enrollments"
    )
    date_enrolled = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.class_grade} ({self.section})"


class Classroom(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="classrooms"
    )

    def __str__(self):
        return self.name
