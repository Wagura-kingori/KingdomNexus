from django.db import models
from students.models import Student
from teachers.models import Teacher


class Hostel(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    warden = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class HostelRoom(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=20)
    capacity = models.IntegerField(default=1)

    def current_occupancy(self):
        return Boarder.objects.filter(room=self).count()

    def available_beds(self):
        return self.capacity - self.current_occupancy()

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room_number}"


class Boarder(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(HostelRoom, on_delete=models.SET_NULL, null=True)
    bed_number = models.IntegerField(default=1)
    date_joined = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ["room", "bed_number"]

    def __str__(self):
        return f"{self.student} ({self.room})"
