
from datetime import datetime, timezone
from app.repositories.memory import (
    missions,
    mission_ships,
    requests,
    generate_id
)
from app.schemas.mission import MissionStatus
from app.services.mission_event import register_event

def get_mission_seat_summary(mission_id):
    mission = missions.get(mission_id)

    if mission is None:
        raise ValueError("Missão não encontrada")

    mission_requests = [
        request for request in requests.values()
        if request["mission_id"] == mission_id
    ]

    confirmed = sum(
        request["confirmed_seats"]
        for request in mission_requests
    )

    pending = sum(
        request["requested_seats"]
        for request in mission_requests
        if request["status"] == "PENDING"
    )

    missing = max(0, mission["people_count"] - confirmed)

    uncommitted = max(0, mission["people_count"] - confirmed - pending)

    return {
        "people_count": mission["people_count"],
        "confirmed_seats": confirmed,
        "pending_seats": pending,
        "missing_seats": missing,
        "uncommitted_seats": uncommitted
    }

def create_request(
    mission_id,
    mission_ship_id,
    requested_seats,
    expires_at=None
):
    mission = missions.get(mission_id)

    if mission is None:
        raise ValueError("Missão não encontrada")

    association = mission_ships.get(mission_ship_id)

    if association is None:
        raise ValueError("Associação de nave não encontrada")

    if association["mission_id"] != mission_id:
        raise ValueError("A nave não pertence a esta missão")

    if association["status"] != "AVAILABLE":
        raise ValueError("Esta associação não está disponível")

    if requested_seats <= 0:
        raise ValueError("A quantidade solicitada deve ser positiva")

    if requested_seats > association["offered_seats"]:
        raise ValueError("A quantidade solicitada supera a oferta da nave")

    summary = get_mission_seat_summary(mission_id)

    if requested_seats > summary["uncommitted_seats"]:
        raise ValueError("Não há assentos suficientes ainda não comprometidos")

    request_id = generate_id("requests")

    request = {
        "id": request_id,
        "mission_id": mission_id,
        "mission_ship_id": mission_ship_id,
        "requested_seats": requested_seats,
        "confirmed_seats": 0,
        "status": "PENDING",
        "created_at": datetime.now(timezone.utc),
        "responded_at": None,
        "expires_at": expires_at
    }

    requests[request_id] = request

    association["status"] = "REQUESTED"
    mission["status"] = MissionStatus.IN_PROGRESS

    register_event(
        mission_id,
        "REQUEST_CREATED",
        f"Solicitados {requested_seats} assentos à nave",
        request_id=request_id
    )

    return request

def register_response(request_id, confirmed_seats):
    request = requests.get(request_id)

    if request is None:
        raise ValueError("Solicitação não encontrada")

    if request["status"] != "PENDING":
        raise ValueError("Esta solicitação já foi encerrada")

    if confirmed_seats < 0:
        raise ValueError("A confirmação não pode ser negativa")

    if confirmed_seats > request["requested_seats"]:
        raise ValueError("Não é possível confirmar mais assentos que o solicitado")

    if confirmed_seats == request["requested_seats"]:
        status = "CONFIRMED"
    elif confirmed_seats > 0:
        status = "PARTIAL"
    else:
        status = "REFUSED"

    request["confirmed_seats"] = confirmed_seats
    request["status"] = status
    request["responded_at"] = datetime.now(timezone.utc)

    mission_ships[request["mission_ship_id"]]["status"] = "UNAVAILABLE"

    mission_id = request["mission_id"]

    register_event(
        mission_id,
        "REQUEST_RESPONSE",
        f"Solicitação respondida: {status}",
        request_id=request_id,
        details={
            "confirmed_seats": confirmed_seats
        }
    )

    summary = get_mission_seat_summary(mission_id)

    if summary["confirmed_seats"] >= summary["people_count"]:
        missions[mission_id]["status"] = MissionStatus.COMPLETED

        register_event(
            mission_id,
            "MISSION_COMPLETED",
            "Todos os assentos necessários foram confirmados"
        )

    return request

def cancel_request(request_id):
    request = requests.get(request_id)

    if request is None:
        raise ValueError("Solicitação não encontrada")

    if request["status"] != "PENDING":
        raise ValueError("Apenas solicitações pendentes podem ser canceladas")

    request["status"] = "CANCELLED"

    register_event(
        request["mission_id"],
        "REQUEST_CANCELLED",
        "Solicitação cancelada",
        request_id=request_id
    )

    return request

def expire_request(request_id):
    request = requests.get(request_id)

    if request is None:
        raise ValueError("Solicitação não encontrada")

    if request["status"] != "PENDING":
        raise ValueError("Apenas solicitações pendentes podem expirar")

    if request["expires_at"] is None:
        raise ValueError("Solicitação não possui prazo de expiração")

    now = datetime.now(timezone.utc)

    if request["expires_at"] > now:
        raise ValueError("O prazo da solicitação ainda não terminou")

    request["status"] = "EXPIRED"

    register_event(
        request["mission_id"],
        "REQUEST_EXPIRED",
        "Solicitação expirada por falta de resposta",
        request_id=request_id
    )

    return request

def list_requests(mission_id=None):
    all_requests = list(requests.values())

    if mission_id is not None:
        all_requests = [
            request for request in all_requests
            if request["mission_id"] == mission_id
        ]

    return all_requests

def get_request(request_id):
    return requests.get(request_id)