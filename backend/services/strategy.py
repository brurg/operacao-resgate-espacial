from datetime import datetime, timezone
from backend.repositories.memory import (
    missions,
    mission_ships,
    requests,
    lock
)
from backend.schemas.mission import MissionStatus
from backend.services.rescue_request import (
    get_mission_seat_summary,
    get_ship_available_capacity,
    create_request,
    cancel_pending_request_for_reallocation
)

ETA_LIMIT_MINUTES = 180

URGENCY_PRIORITY = {
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3
}

def get_value(value):
    return getattr(value, "value", value)

def normalize_datetime(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)

    return value

def get_priority(mission):
    urgency = get_value(
        mission.get("urgency", "MEDIUM")
    )

    return URGENCY_PRIORITY.get(urgency, 2)

def get_eta_minutes(arrival_time):
    arrival = normalize_datetime(arrival_time)
    now = datetime.now(timezone.utc)

    return max(
        0,
        (arrival - now).total_seconds() / 60
    )

def rank_offers(offers, urgency):
    candidates = []

    for offer in offers:
        offered_capacity = offer["offered_seats"]

        if offered_capacity <= 0:
            continue

        available_capacity = get_ship_available_capacity(
            offer["ship_id"]
        )
        capacity = min(
            offered_capacity,
            available_capacity
        )

        eta = get_eta_minutes(offer["arrival_time"])

        candidates.append({
            "offer": offer,
            "eta": eta,
            "capacity": capacity
        })

    if not candidates:
        return []

    urgency = get_value(urgency)

    if urgency == "HIGH":
        candidates.sort(
            key=lambda item: (
                item["eta"],
                -item["capacity"]
            )
        )

    elif urgency == "LOW":
        candidates.sort(
            key=lambda item: (
                -item["capacity"],
                item["eta"]
            )
        )

    else:
        max_capacity = max(
            item["capacity"]
            for item in candidates
        )

        for item in candidates:
            time_score = 1 / (
                1 + item["eta"] / ETA_LIMIT_MINUTES
            )

            capacity_score = (
                item["capacity"] / max_capacity
            )

            item["score"] = (
                0.5 * time_score
                + 0.5 * capacity_score
            )

        candidates.sort(
            key=lambda item: (
                -item["score"],
                item["eta"],
                -item["capacity"]
            )
        )

    return candidates

def release_lower_priority_requests(
    ship_id,
    current_mission,
    required_capacity
):
    current_priority = get_priority(current_mission)

    pending_requests = []

    for request in requests.values():
        if request["status"] != "PENDING":
            continue

        offer = mission_ships.get(
            request["mission_ship_id"]
        )

        if offer is None or offer["ship_id"] != ship_id:
            continue

        other_mission = missions.get(
            request["mission_id"]
        )

        if other_mission is None:
            continue

        if other_mission["status"] == MissionStatus.COMPLETED:
            continue

        other_priority = get_priority(other_mission)

        if other_priority <= current_priority:
            continue

        pending_requests.append({
            "request": request,
            "priority": other_priority,
            "created_at": normalize_datetime(
                request["created_at"]
            )
        })

    pending_requests.sort(
        key=lambda item: (
            -item["priority"],
            -item["created_at"].timestamp()
        )
    )

    cancelled_requests = []

    for item in pending_requests:
        available_capacity = get_ship_available_capacity(
            ship_id
        )

        if available_capacity >= required_capacity:
            break

        request = item["request"]

        cancel_pending_request_for_reallocation(
            request["id"],
            current_mission["id"]
        )

        cancelled_requests.append(request["id"])

    return cancelled_requests

def execute_strategy(mission_id=None):
    with lock:
        mission_list = [
            mission
            for mission in missions.values()
            if mission["status"] != MissionStatus.COMPLETED
        ]

        mission_list.sort(
            key=lambda mission: (
                get_priority(mission),
                normalize_datetime(mission["created_at"])
            )
        )

        results = []

        for mission in mission_list:
            summary = get_mission_seat_summary(
                mission["id"]
            )

            remaining = summary["uncommitted_seats"]

            if remaining <= 0:
                continue

            available_offers = [
                offer
                for offer in mission_ships.values()
                if (
                    offer["mission_id"] == mission["id"]
                    and offer["status"] == "AVAILABLE"
                )
            ]

            ranked_offers = rank_offers(
                available_offers,
                mission.get("urgency", "MEDIUM")
            )

            created_requests = []
            cancelled_requests = []

            for candidate in ranked_offers:
                if remaining <= 0:
                    break

                offer = candidate["offer"]

                required_capacity = min(
                    remaining,
                    offer["offered_seats"]
                )

                current_capacity = get_ship_available_capacity(
                    offer["ship_id"]
                )

                if current_capacity < required_capacity:
                    cancelled = release_lower_priority_requests(
                        offer["ship_id"],
                        mission,
                        required_capacity
                    )

                    cancelled_requests.extend(cancelled)

                    current_capacity = get_ship_available_capacity(
                        offer["ship_id"]
                    )

                seats_to_request = min(
                    remaining,
                    offer["offered_seats"],
                    current_capacity
                )

                if seats_to_request <= 0:
                    continue

                request = create_request(
                    mission_id=mission["id"],
                    mission_ship_id=offer["id"],
                    requested_seats=seats_to_request
                )

                created_requests.append(request)
                remaining -= seats_to_request

            if created_requests or cancelled_requests:
                results.append({
                    "mission_id": mission["id"],
                    "mission_name": mission["name"],
                    "urgency": get_value(
                        mission.get("urgency", "MEDIUM")
                    ),
                    "requests_created": created_requests,
                    "requests_cancelled": cancelled_requests,
                    "uncommitted_seats_remaining": remaining
                })

        return results