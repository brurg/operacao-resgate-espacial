from datetime import datetime, timezone
from backend.repositories.memory import (
    missions,
    ships,
    mission_ships,
    requests,
    generate_id,
    lock
)
from backend.schemas.mission import MissionStatus
from backend.services.mission_event import register_event


def get_mission_seat_summary(mission_id):
    with lock:
        mission = missions.get(mission_id)

        if mission is None:
            raise ValueError("Missão não encontrada")

        mission_requests = [
            request
            for request in requests.values()
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

def get_ship_committed_seats(ship_id):
    with lock:
        committed = 0

        for request in requests.values():
            offer = mission_ships.get(request["mission_ship_id"])

            if offer is None or offer["ship_id"] != ship_id:
                continue

            if request["status"] == "PENDING":
                committed += request["requested_seats"]

            elif request["status"] in ("CONFIRMED", "PARTIAL"):
                committed += request["confirmed_seats"]

        return committed

def get_ship_available_capacity(ship_id):
    with lock:
        ship = ships.get(ship_id)

        if ship is None:
            raise ValueError("Nave não encontrada")

        committed = get_ship_committed_seats(ship_id)

        return max(0, ship["total_capacity"] - committed)

def create_request(mission_id, mission_ship_id, requested_seats, expires_at=None):
    with lock:
        mission = missions.get(mission_id)

        if mission is None:
            raise ValueError("Missão não encontrada")

        if mission["status"] == MissionStatus.COMPLETED:
            raise ValueError("A missão já foi concluída")

        offer = mission_ships.get(mission_ship_id)

        if offer is None:
            raise ValueError("Disponibilidade de nave não encontrada")

        if offer["mission_id"] != mission_id:
            raise ValueError("A nave não pertence a esta missão")

        if offer["status"] != "AVAILABLE":
            raise ValueError("Esta oferta não está disponível")

        if (
            not isinstance(requested_seats, int)
            or isinstance(requested_seats, bool)
        ):
            raise ValueError(
                "A quantidade solicitada deve ser um número inteiro"
            )

        if requested_seats <= 0:
            raise ValueError("A quantidade solicitada deve ser positiva")

        if requested_seats > offer["offered_seats"]:
            raise ValueError(
                "A quantidade solicitada supera a oferta da nave"
            )

        summary = get_mission_seat_summary(mission_id)

        if requested_seats > summary["uncommitted_seats"]:
            raise ValueError(
                "Não há assentos suficientes ainda não comprometidos"
            )

        available_capacity = get_ship_available_capacity(offer["ship_id"])

        if requested_seats > available_capacity:
            raise ValueError(
                "A nave não possui capacidade disponível suficiente"
            )

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

        offer["status"] = "REQUESTED"
        mission["status"] = MissionStatus.IN_PROGRESS

        register_event(
            mission_id,
            "REQUEST_CREATED",
            f"Solicitação de {requested_seats} assentos criada para a nave {offer['ship_name']}",
            details={
                "request_id": request_id,
                "mission_ship_id": mission_ship_id,
                "requested_seats": requested_seats
            }
        )

        return request

def cancel_pending_request_for_reallocation(
    request_id,
    higher_priority_mission_id
):
    with lock:
        request = requests.get(request_id)

        if request is None:
            raise ValueError("Solicitação não encontrada")

        if request["status"] != "PENDING":
            raise ValueError(
                "Apenas solicitações pendentes podem ser realocadas"
            )

        offer = mission_ships.get(
            request["mission_ship_id"]
        )

        if offer is None:
            raise ValueError(
                "Disponibilidade de nave não encontrada"
            )

        request["status"] = "CANCELLED"
        request["responded_at"] = datetime.now(timezone.utc)

        offer["status"] = "AVAILABLE"

        register_event(
            request["mission_id"],
            "REQUEST_CANCELLED",
            "Solicitação cancelada automaticamente para priorizar uma missão de maior urgência",
            details={
                "request_id": request_id,
                "higher_priority_mission_id": higher_priority_mission_id,
                "mission_ship_id": offer["id"],
                "ship_id": offer["ship_id"],
                "automatic_reallocation": True
            }
        )

        return request

def register_response(request_id, confirmed_seats):
    with lock:
        request = requests.get(request_id)

        if request is None:
            raise ValueError("Solicitação não encontrada")

        if request["status"] != "PENDING":
            raise ValueError("Esta solicitação já foi encerrada")

        if (
            not isinstance(confirmed_seats, int)
            or isinstance(confirmed_seats, bool)
        ):
            raise ValueError(
                "A quantidade confirmada deve ser um número inteiro"
            )

        if confirmed_seats < 0:
            raise ValueError("A confirmação não pode ser negativa")

        if confirmed_seats > request["requested_seats"]:
            raise ValueError(
                "Não é possível confirmar mais assentos que o solicitado"
            )

        if confirmed_seats == request["requested_seats"]:
            status = "CONFIRMED"
        elif confirmed_seats > 0:
            status = "PARTIAL"
        else:
            status = "UNAVAILABLE"

        request["confirmed_seats"] = confirmed_seats
        request["status"] = status
        request["responded_at"] = datetime.now(timezone.utc)

        offer = mission_ships[request["mission_ship_id"]]
        offer["status"] = "UNAVAILABLE"

        mission_id = request["mission_id"]

        register_event(
            mission_id,
            "REQUEST_RESPONDED",
            f"Solicitação respondida: {status}",
            details={
                "request_id": request_id,
                "confirmed_seats": confirmed_seats,
                "status": status
            }
        )

        summary = get_mission_seat_summary(mission_id)

        if summary["confirmed_seats"] == summary["people_count"]:
            missions[mission_id]["status"] = MissionStatus.COMPLETED

            register_event(
                mission_id,
                "MISSION_COMPLETED",
                "Missão concluída: todos os assentos necessários foram confirmados",
                details=summary
            )

        else:
            from backend.services.strategy import execute_strategy
            execute_strategy()

        return request

def cancel_request(request_id):
    with lock:
        request = requests.get(request_id)

        if request is None:
            raise ValueError("Solicitação não encontrada")

        if request["status"] != "PENDING":
            raise ValueError(
                "Apenas solicitações pendentes podem ser canceladas"
            )

        request["status"] = "CANCELLED"

        offer = mission_ships[request["mission_ship_id"]]
        offer["status"] = "UNAVAILABLE"

        mission_id = request["mission_id"]

        register_event(
            mission_id,
            "REQUEST_CANCELLED",
            "Solicitação cancelada",
            details={"request_id": request_id}
        )
        from backend.services.strategy import execute_strategy
        execute_strategy()

        return request

def expire_request(request_id):
    with lock:
        request = requests.get(request_id)

        if request is None:
            raise ValueError("Solicitação não encontrada")

        if request["status"] != "PENDING":
            raise ValueError(
                "Apenas solicitações pendentes podem expirar"
            )

        if request["expires_at"] is None:
            raise ValueError(
                "Solicitação não possui prazo de expiração"
            )

        now = datetime.now(timezone.utc)
        expires_at = request["expires_at"]

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at > now:
            raise ValueError(
                "O prazo da solicitação ainda não terminou"
            )

        request["status"] = "EXPIRED"

        offer = mission_ships[request["mission_ship_id"]]
        offer["status"] = "UNAVAILABLE"

        mission_id = request["mission_id"]

        register_event(
            mission_id,
            "REQUEST_EXPIRED",
            "Solicitação expirada",
            details={"request_id": request_id}
        )

        from backend.services.strategy import execute_strategy
        execute_strategy()

        return request

def list_requests(mission_id=None):
    with lock:
        all_requests = list(requests.values())

        if mission_id is not None:
            all_requests = [
                request
                for request in all_requests
                if request["mission_id"] == mission_id
            ]

        return all_requests

def get_request(request_id):
    with lock:
        return requests.get(request_id)