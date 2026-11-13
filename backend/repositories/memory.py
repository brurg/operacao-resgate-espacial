missions = {}
ships = {
    1: {
        "id": 1,
        "name": "Nave Alpha",
        "total_capacity": 12
    },
    2: {
        "id": 2,
        "name": "Nave Beta",
        "total_capacity": 17
    },
    3: {
        "id": 3,
        "name": "Nave Gamma",
        "total_capacity": 5
    }
}

mission_ships = {}
requests = {}
events = {}

counters = {
    "missions": 0,
    "ships": 3,
    "mission_ships": 0,
    "requests": 0,
    "events": 0
}

def generate_id(entity):
    counters[entity] += 1
    return counters[entity]