from django.db import models


from django.urls import reverse
class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.TextField(max_length=500)
    description = models.TextField()
    cover = models.ImageField(upload_to='projects/covers/', blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return self.title
    


def get_absolute_url(self):
    return reverse('project_detail', kwargs={'slug': self.slug})


class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact_phone = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    established_year = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

    @property
    def student_count(self):
        return self.students.count()

    @property
    def teacher_count(self):
        return self.teachers.count()

    @property
    def achievement_count(self):
        return self.achievements.count()


class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="students")
    full_name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=100, unique=True)
    age = models.PositiveIntegerField()
    class_level = models.CharField(max_length=50)  # Example: "Grade 6", "Form 2"
    date_joined = models.DateField()

    def __str__(self):
        return f"{self.full_name} ({self.admission_number})"


class Teacher(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teachers")
    full_name = models.CharField(max_length=255)
    staff_id = models.CharField(max_length=100, unique=True)
    subject = models.CharField(max_length=100)  # Example: "Mathematics"
    hire_date = models.DateField()

    def __str__(self):
        return f"{self.full_name} - {self.subject}"


class Achievement(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="achievements")
    title = models.CharField(max_length=255)
    description = models.TextField()
    year = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.title} ({self.year})"

class GalleryImage(models.Model):
    title = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='gallery/')
    caption = models.CharField(max_length=300, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)


def __str__(self):
    return self.title or f'Image {self.id}'


class Sermon(models.Model):
    title = models.CharField(max_length=255)
    preacher = models.CharField(max_length=200, blank=True)
    date = models.DateField()
    video_url = models.URLField(blank=True, help_text='YouTube or Vimeo embed link')
    audio_file = models.FileField(upload_to='sermons/audio/', blank=True)
    notes = models.TextField(blank=True)


def __str__(self):
    return f"{self.title} — {self.date}"


class Donation(models.Model):
    name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_charge_id = models.CharField(max_length=200, blank=True)


def __str__(self):
    return f"{self.amount} by {self.name or 'Anonymous'}"

# class PrayerRequest(models.Model):
#     name = models.CharField(max_length=150)
#     email = models.EmailField(blank=True, null=True)
#     message = models.TextField()
#     submitted_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Prayer from {self.name}"

class Event(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    date = models.DateField()
    time = models.CharField(max_length=50, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    short_description = models.TextField()
    description = models.TextField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("event_detail", args=[self.slug])

class Pastor(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=150)
    photo = models.ImageField(upload_to="pastors/")
    short_bio = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
class PrayerRequest(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True, null=True)
    subject = models.CharField(max_length=250, blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)   # mark handled requests
    notified = models.BooleanField(default=False)  # email notification sent
   


    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Prayer from {self.name or 'Anonymous'} ({self.submitted_at:%Y-%m-%d %H:%M})"

