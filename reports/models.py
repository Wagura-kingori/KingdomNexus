from django.db import models

# Create your models here.
from schools.models import School
school = models.ForeignKey(School, on_delete=models.CASCADE)