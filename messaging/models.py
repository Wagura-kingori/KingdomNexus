from django.db import models
from django.conf import settings
from profiles.models import StudentProfile, ParentProfile

class Notice(models.Model):
    NOTICE_TYPES = [
        ('general', 'General Notice'),
        ('class', 'Class Notice'),
        ('student', 'Student Notice'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    notice_type = models.CharField(max_length=20, choices=NOTICE_TYPES)
    target_class = models.ForeignKey('students.ClassRoom', null=True, blank=True, on_delete=models.SET_NULL)
    target_student = models.ForeignKey(StudentProfile, null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.subject
