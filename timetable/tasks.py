from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta, date
import random


def time_to_minutes(t) -> int:
    """Convert a time object to minutes since midnight."""
    return t.hour * 60 + t.minute


def minutes_to_time(minutes: int):
    """Convert minutes since midnight to a time object."""
    from datetime import time
    return time(minutes // 60, minutes % 60)


def times_overlap(start1, end1, start2, end2) -> bool:
    """Check if two time ranges overlap."""
    return start1 < end2 and start2 < end1


@shared_task(bind=True)
def generate_master_timetable(self, job_id: int):
    """
    Auto-generate the master timetable for a school.
    Uses a greedy algorithm with conflict detection.
    """
    from .models import (
        TimetableGenerationJob,
        TimetableGenerationConfig,
        ClassroomSubjectConfig,
        MasterTimetableEntry,
        Period,
    )
    from datetime import time

    job = TimetableGenerationJob.objects.get(id=job_id)
    job.status = "running"
    job.save()

    try:
        config = TimetableGenerationConfig.objects.prefetch_related(
            'breaks', 'subject_configs__classroom',
            'subject_configs__subject', 'subject_configs__teacher'
        ).get(school=job.school, academic_year=job.academic_year)

        days = config.days or [
            "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"
        ]
        lesson_duration = config.lesson_duration
        breaks = list(config.breaks.all())

        # Build list of available slots for the day
        def get_day_slots():
            slots = []
            current = time_to_minutes(config.school_start_time)
            end = time_to_minutes(config.school_end_time)

            while current + lesson_duration <= end:
                slot_start = minutes_to_time(current)
                slot_end = minutes_to_time(current + lesson_duration)

                # Check if this slot overlaps with any break
                overlaps_break = any(
                    times_overlap(
                        slot_start, slot_end,
                        b.start_time, b.end_time
                    )
                    for b in breaks
                )

                if not overlaps_break:
                    slots.append((slot_start, slot_end))
                    current += lesson_duration
                else:
                    # Skip to end of the overlapping break
                    for b in breaks:
                        if times_overlap(
                            slot_start, slot_end,
                            b.start_time, b.end_time
                        ):
                            current = time_to_minutes(b.end_time)
                            break

            return slots

        day_slots = get_day_slots()

        # Clear existing auto-generated entries for this school/year
        MasterTimetableEntry.objects.filter(
            school=job.school,
            academic_year=job.academic_year
        ).delete()

        # Track allocations
        # teacher_busy[teacher_id][(day, start_time)] = True
        teacher_busy = {}
        # classroom_busy[classroom_id][(day, start_time)] = True
        classroom_busy = {}

        entries_to_create = []
        conflicts = []

        subject_configs = list(
            config.subject_configs.select_related(
                'classroom', 'subject', 'teacher'
            ).all()
        )

        # Group configs by classroom
        from collections import defaultdict
        classroom_configs = defaultdict(list)
        for sc in subject_configs:
            classroom_configs[sc.classroom.id].append(sc)

        # Process fixed slots first across all classrooms
        for sc in subject_configs:
            if not sc.is_fixed or not sc.fixed_day or not sc.fixed_start_time:
                continue

            teacher_id = sc.teacher.id
            classroom_id = sc.classroom.id

            # Find matching slot end time
            fixed_start = sc.fixed_start_time
            fixed_end = minutes_to_time(
                time_to_minutes(fixed_start) + lesson_duration
            )

            slot_key = (sc.fixed_day, fixed_start.strftime('%H:%M'))

            # If school-wide fixed, apply to all classrooms with same subject
            if sc.fixed_scope == 'school':
                same_subject_configs = [
                    s for s in subject_configs
                    if s.subject.id == sc.subject.id and s.is_fixed
                    and s.fixed_day == sc.fixed_day
                    and s.fixed_start_time == sc.fixed_start_time
                ]
                for same_sc in same_subject_configs:
                    t_id = same_sc.teacher.id
                    c_id = same_sc.classroom.id
                    t_busy = teacher_busy.setdefault(t_id, {})
                    c_busy = classroom_busy.setdefault(c_id, {})
                    s_key = (same_sc.fixed_day, fixed_start.strftime('%H:%M'))

                    if s_key in t_busy:
                        conflicts.append(
                            f"Teacher {same_sc.teacher} conflict on "
                            f"{same_sc.fixed_day} {fixed_start} "
                            f"(fixed slot clash)"
                        )
                        continue
                    if s_key in c_busy:
                        conflicts.append(
                            f"Classroom {same_sc.classroom} conflict on "
                            f"{same_sc.fixed_day} {fixed_start} "
                            f"(fixed slot clash)"
                        )
                        continue

                    t_busy[s_key] = True
                    c_busy[s_key] = True
                    entries_to_create.append(
                        MasterTimetableEntry(
                            school=job.school,
                            teacher=same_sc.teacher,
                            subject=same_sc.subject,
                            classroom=same_sc.classroom,
                            day=same_sc.fixed_day,
                            start_time=fixed_start,
                            end_time=fixed_end,
                            academic_year=job.academic_year,
                        )
                    )
            else:
                t_busy = teacher_busy.setdefault(teacher_id, {})
                c_busy = classroom_busy.setdefault(classroom_id, {})

                if slot_key in t_busy:
                    conflicts.append(
                        f"Teacher {sc.teacher} conflict on "
                        f"{sc.fixed_day} {fixed_start} (fixed slot clash)"
                    )
                    continue
                if slot_key in c_busy:
                    conflicts.append(
                        f"Classroom {sc.classroom} conflict on "
                        f"{sc.fixed_day} {fixed_start} (fixed slot clash)"
                    )
                    continue

                t_busy[slot_key] = True
                c_busy[slot_key] = True
                entries_to_create.append(
                    MasterTimetableEntry(
                        school=job.school,
                        teacher=sc.teacher,
                        subject=sc.subject,
                        classroom=sc.classroom,
                        day=sc.fixed_day,
                        start_time=fixed_start,
                        end_time=fixed_end,
                        academic_year=job.academic_year,
                    )
                )

        # Now place non-fixed subjects
        for classroom_id, configs_list in classroom_configs.items():
            # Sort by lessons_per_week descending (place busier subjects first)
            non_fixed = sorted(
                [sc for sc in configs_list if not sc.is_fixed],
                key=lambda x: x.lessons_per_week,
                reverse=True
            )

            for sc in non_fixed:
                teacher_id = sc.teacher.id
                t_busy = teacher_busy.setdefault(teacher_id, {})
                c_busy = classroom_busy.setdefault(classroom_id, {})

                lessons_placed = 0
                lessons_needed = sc.lessons_per_week

                # Track which days this subject has been placed
                # (for even distribution)
                days_used = set()

                # Shuffle days to avoid always starting Monday
                shuffled_days = days.copy()
                random.shuffle(shuffled_days)

                for day in shuffled_days * 2:  # allow multiple passes
                    if lessons_placed >= lessons_needed:
                        break

                    # Don't place same subject twice on same day
                    # unless lessons_per_week > len(days)
                    if day in days_used and lessons_needed <= len(days):
                        continue

                    for slot_start, slot_end in day_slots:
                        if lessons_placed >= lessons_needed:
                            break

                        slot_key = (day, slot_start.strftime('%H:%M'))

                        if slot_key in t_busy:
                            continue
                        if slot_key in c_busy:
                            continue

                        # Place the lesson
                        t_busy[slot_key] = True
                        c_busy[slot_key] = True
                        days_used.add(day)
                        lessons_placed += 1

                        entries_to_create.append(
                            MasterTimetableEntry(
                                school=job.school,
                                teacher=sc.teacher,
                                subject=sc.subject,
                                classroom=sc.classroom,
                                day=day,
                                start_time=slot_start,
                                end_time=slot_end,
                                academic_year=job.academic_year,
                            )
                        )

                if lessons_placed < lessons_needed:
                    conflicts.append(
                        f"Could only place {lessons_placed}/{lessons_needed} "
                        f"lessons for {sc.subject} in {sc.classroom} "
                        f"(not enough free slots)"
                    )

        # Bulk create all entries
        MasterTimetableEntry.objects.bulk_create(
            entries_to_create,
            ignore_conflicts=True
        )

        job.status = "completed"
        job.completed_at = timezone.now()
        job.entries_created = len(entries_to_create)
        job.conflicts = conflicts
        job.save()

        return {
            "status": "completed",
            "entries_created": len(entries_to_create),
            "conflicts": conflicts,
        }

    except Exception as e:
        import traceback
        job.status = "failed"
        job.error_message = traceback.format_exc()
        job.completed_at = timezone.now()
        job.save()
        raise