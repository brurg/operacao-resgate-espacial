from datetime import datetime, timezone
from backend.repositories.memory import (
    events,
    generate_id,
    lock
)

def register_event(
    mission_id,
    event_type,
    description,
    request_id=None,
    details=None
):
    with lock:
        event_id = generate_id("events")

        event = {
            "id": event_id,
            "mission_id": mission_id,
            "request_id": request_id,
            "event_type": event_type,
            "description": description,
            "timestamp": datetime.now(timezone.utc),
            "details": details or {}
        }

        events[event_id] = event

        return event

def list_mission_events(mission_id):
    with lock:
        mission_events = [
            event
            for event in events.values()
            if event["mission_id"] == mission_id
        ]

        return sorted(
            mission_events,
            key=lambda event: event["timestamp"]
        )

def get_event(event_id):
    with lock:
        return events.get(event_id)