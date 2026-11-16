
from backend.repositories.memory import missions, ships, mission_ships, generate_id
from backend.services.mission_event import register_event
from backend.services.rescue_request import get_mission_seat_summary

def offer_ship(
    mission_id,
    ship_id,
    offered_seats,
    arrival_time
):
    mission = missions.get(mission_id)

    if mission is None:
        raise ValueError("Missão não encontrada")

    ship = ships.get(ship_id)

    if ship is None:
        raise ValueError("Nave não encontrada")

    if mission["status"] == "COMPLETED":
        raise ValueError(
            "Não é possível disponibilizar naves para uma missão concluída"
        )

    summary = get_mission_seat_summary(mission_id)

    if summary["missing_seats"] <= 0:
        raise ValueError(
            "Não há mais necessidade de assentos para esta missão"
        )

    if offered_seats <= 0:
        raise ValueError("A quantidade de assentos deve ser positiva")

    if offered_seats > ship["total_capacity"]:
        raise ValueError(
            "A quantidade oferecida supera a capacidade da nave"
        )

    for offer in mission_ships.values():
        if (
            offer["mission_id"] == mission_id
            and offer["ship_id"] == ship_id
        ):
            raise ValueError(
                "Nave já disponibilizada a esta missão"
            )

    offer_id = generate_id("mission_ships")

    offer = {
        "id": offer_id,
        "mission_id": mission_id,
        "ship_id": ship_id,
        "ship_name": ship["name"],
        "offered_seats": offered_seats,
        "arrival_time": arrival_time,
        "status": "AVAILABLE"
    }

    mission_ships[offer_id] = offer

    register_event(
        mission_id,
        "SHIP_OFFERED",
        f"Nave {ship['name']} disponibilizada à missão",
        details={
            "ship_id": ship_id,
            "offered_seats": offered_seats,
            "arrival_time": str(arrival_time)
        }
    )

    return offer

def list_mission_ships(mission_id):
    return [
        offer
        for offer in mission_ships.values()
        if offer["mission_id"] == mission_id
    ]

def get_mission_ship(offer_id):
    return mission_ships.get(offer_id)
