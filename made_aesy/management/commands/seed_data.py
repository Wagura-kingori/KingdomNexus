from django.core.management.base import BaseCommand
from faker import Faker
import random
from made_aesy.models import School, Student, Teacher, Achievement

class Command(BaseCommand):
    help = "Populate database with dummy school data"

    def handle(self, *args, **kwargs):
        fake = Faker()

        # Clean old data (optional)
        School.objects.all().delete()

        # Create 3 schools
        for _ in range(3):
            school = School.objects.create(
                name=fake.company() + " School",
                address=fake.address(),
                contact_phone=fake.phone_number(),
                description=fake.text(),
                established_year=random.randint(1960, 2020)
            )

            # Create 20–55 students per school
            for _ in range(random.randint(20, 55)):
                Student.objects.create(
                    school=school,
                    full_name=fake.name(),
                    admission_number=f"ADM{fake.unique.random_int(min=1000, max=999999)}",

                    age=random.randint(6, 18),
                    class_level=random.choice(["Grade 4", "Grade 6", "Form 1", "Form 2", "Form 3"]),
                    date_joined=fake.date_between(start_date='-5y', end_date='today')
                )

            # Create 15–30 teachers per school
            for _ in range(random.randint(15, 30)):
                Teacher.objects.create(
                    school=school,
                    full_name=fake.name(),
                
                    staff_id=f"TS{fake.unique.random_int(min=1000, max=999999)}",

                    subject=random.choice(["Math", "English", "Science", "History", "Geography"]),
                    hire_date=fake.date_between(start_date='-10y', end_date='today')
                )

            # Create 5–12 achievements per school
            for _ in range(random.randint(5, 12)):
                Achievement.objects.create(
                    school=school,
                    title=fake.sentence(nb_words=5),
                    description=fake.paragraph(),
                    year=random.randint(2000, 2024)
                )

        self.stdout.write(self.style.SUCCESS("Dummy school data created successfully!"))
