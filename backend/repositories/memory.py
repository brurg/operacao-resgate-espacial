from threading import RLock

lock = RLock()

missions = {}

ships = {
    1: {
        "id": 1,
        "name": "Alpha",
        "total_capacity": 10
    },
    2: {
        "id": 2,
        "name": "Beta",
        "total_capacity": 8
    }
}

mission_ships = {}
requests = {}
events = {}

counters = {
    "missions": 0,
    "ships": 2,
    "mission_ships": 0,
    "requests": 0,
    "events": 0
}

def generate_id(entity):
    counters[entity] += 1
    return counters[entity]
