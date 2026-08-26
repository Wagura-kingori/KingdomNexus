"""
Usage: python manage.py publish_term_start T3-2025 2025-09-01 2025-12-05

Publishes a term.started event so fees-service seeds a StudentFeeAccount
for every active student in the new term. Run this once per term, after
the term record itself is created on the Django side.
"""

from datetime import date

from django.core.management.base import BaseCommand, CommandError

from student_sync import publisher


class Command(BaseCommand):
    help = "Publish a term.started event to the fees-service Redis Stream"

    def add_arguments(self, parser):
        parser.add_argument("term", type=str, help='e.g. "T3-2025"')
        parser.add_argument("start_date", type=str, help="YYYY-MM-DD")
        parser.add_argument("end_date", type=str, help="YYYY-MM-DD")

    def handle(self, *args, **options):
        try:
            start = date.fromisoformat(options["start_date"])
            end = date.fromisoformat(options["end_date"])
        except ValueError as exc:
            raise CommandError(f"Dates must be YYYY-MM-DD: {exc}")

        event_id = publisher.term_started(options["term"], start, end)
        self.stdout.write(self.style.SUCCESS(
            f"Published term.started for {options['term']} (event_id={event_id})"
        ))
