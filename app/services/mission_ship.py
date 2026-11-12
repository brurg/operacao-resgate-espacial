
from app.repositories.memory import missions, ships, mission_ships, generate_id
from app.services.mission_event import register_event

def associate_ship(
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

    if mission["status"] != "CREATED":
        raise ValueError(
            "Não é possível associar naves após a missão ser criada"
        )

    if offered_seats <= 0:
        raise ValueError("A quantidade de assentos deve ser positiva")

    if offered_seats > ship["total_capacity"]:
        raise ValueError(
            "A quantidade oferecida supera a capacidade da nave"
        )

    for association in mission_ships.values():
        if (
            association["mission_id"] == mission_id
            and association["ship_id"] == ship_id
        ):
            raise ValueError(
                "Nave já associada a esta missão"
            )

    association_id = generate_id("mission_ships")

    association = {
        "id": association_id,
        "mission_id": mission_id,
        "ship_id": ship_id,
        "offered_seats": offered_seats,
        "arrival_time": arrival_time,
        "status": "AVAILABLE"
    }

    mission_ships[association_id] = association

    register_event(
        mission_id,
        "SHIP_ASSOCIATED",
        f"Nave {ship['name']} associada à missão",
        details={
            "ship_id": ship_id,
            "offered_seats": offered_seats,
            "arrival_time": str(arrival_time)
        }
    )

    return association

def list_mission_ships(mission_id):
    return [
        association
        for association in mission_ships.values()
        if association["mission_id"] == mission_id
    ]

def get_mission_ship(association_id):
    return mission_ships.get(association_id)
