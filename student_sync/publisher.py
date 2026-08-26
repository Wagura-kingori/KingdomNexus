"""
Publishes student lifecycle events to the same Redis Stream the Spring
Boot fees-service consumes (see fees-service's StudentEventListener and
README.md "Event contract").

Wire format (one Redis Stream entry per event, fields are flat strings —
Redis Streams don't support nested types):

    event_id       - uuid4 string, unique per event
    event_type     - "student.enrolled" | "student.updated" |
                      "student.withdrawn" | "term.started"
    occurred_at    - ISO 8601 UTC timestamp
    schema_version - "1" (bump if the payload shape changes incompatibly)
    data           - JSON string, shape depends on event_type (see below)

data for student.enrolled / student.updated:
    {
        "studentId": "STU-1001",
        "name": "Amara Okafor",
        "grade": "Grade 5",
        "guardianPhone": "+254 712 004 118",
        "status": "ACTIVE",
        "term": "T2-2025"          # only meaningful on enrollment
    }

data for student.withdrawn:
    {"studentId": "STU-1001", "withdrawnOn": "2025-11-01"}

data for term.started:
    {"term": "T3-2025", "startDate": "2025-09-01", "endDate": "2025-12-05"}
"""

import json
import uuid
from datetime import datetime, timezone

import redis
from django.conf import settings

STREAM_KEY = getattr(settings, "STUDENT_EVENTS_STREAM_KEY", "kingdomnexus:student-events")

_redis_client = None


def _get_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            getattr(settings, "STUDENT_EVENTS_REDIS_URL", settings.CELERY_BROKER_URL)
        )
    return _redis_client


def _publish(event_type: str, data: dict) -> str:
    """Low-level XADD. Returns the event_id (not the Redis stream record id)."""
    event_id = str(uuid.uuid4())
    fields = {
        "event_id": event_id,
        "event_type": event_type,
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "schema_version": "1",
        "data": json.dumps(data),
    }
    try:
        _get_client().xadd(STREAM_KEY, fields)
    except redis.RedisError:
        # Don't let a broker outage break the request/admin action that
        # triggered this. Log loudly so it's visible in monitoring — a
        # dropped event here means fees-service's StudentRef silently
        # drifts out of sync until the next update event for that student.
        import logging
        logging.getLogger(__name__).exception(
            "Failed to publish %s event %s to Redis Stream '%s'", event_type, event_id, STREAM_KEY
        )
    return event_id


def student_enrolled(student_id: str, name: str, grade, guardian_phone, status: str, term: str) -> str:
    """
    grade and guardian_phone may be None (e.g. a student not yet assigned
    a class, or with no linked parent record) — fees-service treats both
    as optional on the wire.
    """
    return _publish("student.enrolled", {
        "studentId": student_id,
        "name": name,
        "grade": grade,
        "guardianPhone": guardian_phone,
        "status": status,
        "term": term,
    })


def student_updated(student_id: str, name: str, grade, guardian_phone, status: str) -> str:
    return _publish("student.updated", {
        "studentId": student_id,
        "name": name,
        "grade": grade,
        "guardianPhone": guardian_phone,
        "status": status,
    })


def student_withdrawn(student_id: str, withdrawn_on) -> str:
    return _publish("student.withdrawn", {
        "studentId": student_id,
        "withdrawnOn": withdrawn_on.isoformat() if hasattr(withdrawn_on, "isoformat") else str(withdrawn_on),
    })


def term_started(term: str, start_date, end_date) -> str:
    return _publish("term.started", {
        "term": term,
        "startDate": start_date.isoformat() if hasattr(start_date, "isoformat") else str(start_date),
        "endDate": end_date.isoformat() if hasattr(end_date, "isoformat") else str(end_date),
    })
