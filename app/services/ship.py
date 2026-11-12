from app.repositories.memory import ships, generate_id

def create_ship(data):
    ship_id = generate_id("ships")

    ship = {
        "id": ship_id,
        "name": data.name,
        "total_capacity": data.total_capacity
    }
    ships[ship["id"]] = ship

    return ship

def list_ships():
    return list(ships.values())

def get_ship(ship_id):
    return ships.get(ship_id)